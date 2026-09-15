"""Builds the case record (record.json + record.md) from an agent run's own trace.

Every field here is derived from what the trace actually shows happened - tool calls and
their real results - not from re-describing or re-summarizing the model's prose.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agent import AgentResult, ToolCallRecord
from .tools import WRITE_TOOLS

_MONEY_FIELDS_BY_TOOL = {
    "pay_compensation": "amount_gbp",
    "pay_goodwill": "amount_gbp",
    "refund": "amount_gbp",
    "rebook": "fare_gbp",
}


def _is_error(result: Any) -> bool:
    return isinstance(result, dict) and "error" in result and "status_code" in result


def _mode(call: ToolCallRecord) -> str:
    if call.blocked:
        return "blocked"
    if isinstance(call.result, dict) and call.result.get("dry_run"):
        return "dry_run"
    if _is_error(call.result):
        return "failed"
    return "real"


def _money_amount(call: ToolCallRecord) -> float:
    field = _MONEY_FIELDS_BY_TOOL.get(call.name)
    if not field:
        return 0.0
    amount = call.arguments.get(field) or 0.0
    try:
        return float(amount)
    except (TypeError, ValueError):
        return 0.0


def build_record(
    case_id: str,
    inbound_message: str,
    result: AgentResult,
    dry_run: bool,
    input_price_per_1m_usd: float,
    output_price_per_1m_usd: float,
) -> dict:
    trace = result.trace
    reads = [c for c in trace if c.name not in WRITE_TOOLS]
    writes = [c for c in trace if c.name in WRITE_TOOLS and c.name != "escalate"]
    escalations = [c for c in trace if c.name == "escalate"]
    entitlements_calls = [c for c in trace if c.name == "calculate_entitlements" and not c.blocked]

    total_real_paid = sum(_money_amount(c) for c in writes if _mode(c) == "real")
    total_dry_run_would_pay = sum(_money_amount(c) for c in writes if _mode(c) == "dry_run")

    uncertainties: list[str] = []
    for call in trace:
        if call.blocked:
            uncertainties.append(f"{call.name} was blocked by the autonomy guard: {call.result.get('reason')}")
        elif _is_error(call.result):
            uncertainties.append(
                f"{call.name} failed: {call.result.get('error')} - {call.result.get('message')}"
            )
        elif call.name in ("search_availability", "search_availability_partners") and isinstance(
            call.result, dict
        ) and call.result.get("reason") == "service_unavailable":
            uncertainties.append(f"{call.name} was unavailable (503): {call.result.get('message')}")
    for call in entitlements_calls:
        status = call.result.get("status") if isinstance(call.result, dict) else None
        if status in ("INSUFFICIENT_DATA", "NO_DISRUPTION_RECORDED"):
            uncertainties.append(f"calculate_entitlements returned {status} for {call.arguments.get('booking_ref')}")
    if result.escalated_by_cap:
        uncertainties.append(f"Agent hit its {result.iterations}-iteration cap without reaching a natural decision.")

    blocked_calls = [c for c in trace if c.blocked]
    human_followup: list[dict] = []
    for call in escalations:
        human_followup.append(
            {
                "type": "escalation",
                "arguments": call.arguments,
                "result": call.result,
            }
        )
    if blocked_calls and not escalations:
        human_followup.append(
            {
                "type": "unresolved_block",
                "note": "The agent had an action blocked by the autonomy guard but never escalated. "
                "A human needs to pick this case up.",
            }
        )

    escalated = bool(escalations) or result.escalated_by_cap
    escalated_reason = "iteration_cap" if result.escalated_by_cap else ("model_escalated" if escalations else None)

    return {
        "case_id": case_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "inbound_message": inbound_message,
        "decision": {
            "summary": result.decision,
            "escalated": escalated,
            "escalated_reason": escalated_reason,
        },
        "reasoning": {
            "entitlements_consulted": [
                {"arguments": c.arguments, "result": c.result} for c in entitlements_calls
            ],
        },
        "consulted": [{"tool": c.name, "arguments": c.arguments, "result": c.result} for c in reads],
        "actions_taken": [
            {"tool": c.name, "arguments": c.arguments, "result": c.result, "mode": _mode(c)} for c in writes
        ],
        "escalations": [{"arguments": c.arguments, "result": c.result} for c in escalations],
        "money": {
            "total_real_paid_gbp": round(total_real_paid, 2),
            "total_dry_run_would_pay_gbp": round(total_dry_run_would_pay, 2),
        },
        "uncertainties": uncertainties,
        "human_followup": human_followup,
        "trace": [
            {"tool": c.name, "arguments": c.arguments, "result": c.result, "blocked": c.blocked} for c in trace
        ],
        "usage": {
            "prompt_tokens": result.usage.prompt_tokens,
            "completion_tokens": result.usage.completion_tokens,
            "total_tokens": result.usage.total_tokens,
            "model_calls": result.usage.model_calls,
            "estimated_cost_usd": round(
                result.usage.estimated_cost_usd(input_price_per_1m_usd, output_price_per_1m_usd), 6
            ),
            "pricing": {
                "input_per_1m_usd": input_price_per_1m_usd,
                "output_per_1m_usd": output_price_per_1m_usd,
            },
        },
        "run_meta": {
            "iterations": result.iterations,
        },
    }


def _fmt_call(tool: str, arguments: dict, result: Any) -> str:
    body = json.dumps({"arguments": arguments, "result": result}, indent=2, default=str)
    return f"**{tool}**\n```json\n{body}\n```"


def render_markdown(record: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Case record: {record['case_id']}")
    lines.append("")
    lines.append(f"Generated: {record['generated_at']}")
    lines.append(f"Mode: {'DRY RUN (no real actions taken)' if record['dry_run'] else 'LIVE'}")
    usage = record["usage"]
    lines.append(
        f"Tokens: {usage['prompt_tokens']:,} in + {usage['completion_tokens']:,} out = "
        f"{usage['total_tokens']:,} total across {usage['model_calls']} model call(s) - "
        f"estimated cost ${usage['estimated_cost_usd']:.4f}"
    )
    lines.append("")

    lines.append("## 1. Decision - what the passenger gets")
    lines.append("")
    lines.append(record["decision"]["summary"] or "(no decision text produced)")
    lines.append("")
    escalated = record["decision"]["escalated"]
    lines.append(f"Escalated to a human: **{'yes' if escalated else 'no'}**" + (
        f" ({record['decision']['escalated_reason']})" if escalated else ""
    ))
    lines.append("")

    lines.append("## 2. Reasoning - what it rests on")
    lines.append("")
    entitlements = record["reasoning"]["entitlements_consulted"]
    if not entitlements:
        lines.append("calculate_entitlements was never successfully called for this case.")
    for e in entitlements:
        r = e["result"]
        lines.append(f"- `calculate_entitlements` for `{e['arguments'].get('booking_ref')}`: "
                      f"status={r.get('status')}, policy_version={r.get('policy_version')}")
        comp = r.get("compensation", {})
        if comp:
            lines.append(f"  - Compensation: {comp.get('status')} (£{comp.get('amount_gbp')})")
            for clause in comp.get("reasoning", []):
                lines.append(f"    - {clause}")
        for p in r.get("passengers", []):
            for clause in p.get("downgrade_reasoning", []):
                lines.append(f"    - {clause}")
    lines.append("")

    lines.append("## 3. Consulted - every read made")
    lines.append("")
    if not record["consulted"]:
        lines.append("(none)")
    for c in record["consulted"]:
        lines.append(_fmt_call(c["tool"], c["arguments"], c["result"]))
        lines.append("")

    lines.append("## 4. Actions taken - every write, real or dry-run")
    lines.append("")
    if not record["actions_taken"]:
        lines.append("(none)")
    for a in record["actions_taken"]:
        lines.append(f"### {a['tool']} - `{a['mode'].upper()}`")
        lines.append(_fmt_call(a["tool"], a["arguments"], a["result"]))
        lines.append("")
    if record["escalations"]:
        lines.append("### escalate")
        for e in record["escalations"]:
            lines.append(_fmt_call("escalate", e["arguments"], e["result"]))
            lines.append("")
    money = record["money"]
    lines.append(f"Total paid for real: £{money['total_real_paid_gbp']:.2f}")
    lines.append(f"Total that would be paid if this were a live run: £{money['total_dry_run_would_pay_gbp']:.2f}")
    lines.append("")

    lines.append("## 5. Uncertainties")
    lines.append("")
    if not record["uncertainties"]:
        lines.append("None noted.")
    for u in record["uncertainties"]:
        lines.append(f"- {u}")
    lines.append("")

    lines.append("## 6. What a human still needs to do")
    lines.append("")
    if not record["human_followup"]:
        lines.append("Nothing - resolved without escalation.")
    for item in record["human_followup"]:
        if item["type"] == "escalation":
            r = item["result"]
            lines.append(f"- Escalation raised (`{r.get('escalation_id', 'id unknown')}`): "
                          f"{item['arguments'].get('requested_decision')}")
            if item["arguments"].get("queue"):
                lines.append(f"  - Queue: {item['arguments']['queue']}")
            if item["arguments"].get("recommendation"):
                lines.append(f"  - Agent's recommendation: {item['arguments']['recommendation']}")
        else:
            lines.append(f"- {item['note']}")
    lines.append("")

    lines.append("## Raw tool-call trace (in order)")
    lines.append("")
    for i, t in enumerate(record["trace"], 1):
        flag = " [BLOCKED]" if t["blocked"] else ""
        lines.append(f"{i}. `{t['tool']}`{flag}")

    return "\n".join(lines) + "\n"


def write_record(record: dict, output_root: Path) -> tuple[Path, Path]:
    case_dir = Path(output_root) / record["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)

    json_path = case_dir / "record.json"
    json_path.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")

    md_path = case_dir / "record.md"
    md_path.write_text(render_markdown(record), encoding="utf-8")

    return json_path, md_path
