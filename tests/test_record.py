"""Runnable check for record building: mode detection, money totals, uncertainties.

Builds an AgentResult by hand (no OpenAI/ops calls needed) and checks build_record/
render_markdown/write_record derive the right things from it.

Run: python tests/test_record.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from disruption_desk.agent import AgentResult, ToolCallRecord, TokenUsage
from disruption_desk.record import build_record, render_markdown, write_record

INPUT_PRICE = 0.15
OUTPUT_PRICE = 0.60


def build(case_id, inbound, result, dry_run=True):
    return build_record(
        case_id, inbound, result, dry_run=dry_run,
        input_price_per_1m_usd=INPUT_PRICE, output_price_per_1m_usd=OUTPUT_PRICE,
    )


def make_trace():
    return [
        ToolCallRecord("search_bookings", {"q": "AER-4K2P9X"}, {"match_count": 1, "results": [{"booking_ref": "AER-4K2P9X"}]}),
        ToolCallRecord("get_booking", {"booking_ref": "AER-4K2P9X"}, {"booking_ref": "AER-4K2P9X"}),
        ToolCallRecord(
            "calculate_entitlements",
            {"booking_ref": "AER-4K2P9X"},
            {
                "status": "ASSESSED",
                "policy_version": "APCP-2026-04 v11.3",
                "compensation": {"status": "NOT_PAYABLE", "amount_gbp": 0.0, "reasoning": ["S5.1(b): extraordinary cause."]},
                "passengers": [{"downgrade_reasoning": []}],
            },
        ),
        ToolCallRecord(
            "search_availability",
            {"origin": "LHR", "destination": "BCN", "date": "2026-08-04"},
            {"reason": "service_unavailable", "message": "Inventory system did not respond."},
        ),
        ToolCallRecord(
            "pay_goodwill",
            {"booking_ref": "AER-4K2P9X", "amount_gbp": 12.5, "reason": "breakfast + coffees"},
            {"payment_id": "DRYRUN-PAY-1", "amount_gbp": 12.5, "dry_run": True},
        ),
        ToolCallRecord(
            "rebook",
            {"booking_ref": "AER-4K2P9X", "fare_gbp": 500.0},
            {"blocked": True, "reason": "£500.00 exceeds the autonomy limit of £300.00 for a single action. Escalate instead."},
            blocked=True,
        ),
        ToolCallRecord(
            "escalate",
            {"summary": "rebook over threshold", "requested_decision": "authorise upgrade fare", "queue": "SUPERVISOR"},
            {"escalation_id": "ESC-1"},
        ),
    ]


def test_build_record_modes_and_money():
    trace = make_trace()
    result = AgentResult(decision="Priya gets a goodwill payment; rebooking needs sign-off.", trace=trace, iterations=6)
    record = build("case-01", "inbound text", result)

    actions_by_tool = {a["tool"]: a for a in record["actions_taken"]}
    assert actions_by_tool["pay_goodwill"]["mode"] == "dry_run"
    assert actions_by_tool["rebook"]["mode"] == "blocked"
    assert record["money"]["total_dry_run_would_pay_gbp"] == 12.5
    assert record["money"]["total_real_paid_gbp"] == 0.0

    assert len(record["consulted"]) == 4  # search_bookings, get_booking, calculate_entitlements, search_availability
    assert record["escalations"][0]["result"]["escalation_id"] == "ESC-1"
    assert record["decision"]["escalated"] is True
    assert record["decision"]["escalated_reason"] == "model_escalated"

    reasons = " ".join(record["uncertainties"])
    assert "blocked by the autonomy guard" in reasons
    assert "unavailable (503)" in reasons

    assert record["human_followup"][0]["type"] == "escalation"


def test_unresolved_block_flagged_without_escalation():
    trace = [
        ToolCallRecord(
            "pay_goodwill",
            {"booking_ref": "AER-X", "amount_gbp": 500.0, "reason": "x"},
            {"blocked": True, "reason": "over limit"},
            blocked=True,
        ),
    ]
    result = AgentResult(decision="never finished", trace=trace, iterations=1)
    record = build("case-02", "inbound", result)

    assert record["decision"]["escalated"] is False
    assert record["human_followup"][0]["type"] == "unresolved_block"


def test_iteration_cap_marks_escalated():
    result = AgentResult(decision="auto-escalated", trace=[], escalated_by_cap=True, iterations=12)
    record = build("case-03", "inbound", result)
    assert record["decision"]["escalated"] is True
    assert record["decision"]["escalated_reason"] == "iteration_cap"


def test_markdown_and_files_render():
    trace = make_trace()
    result = AgentResult(decision="Priya gets a goodwill payment.", trace=trace, iterations=6)
    record = build("case-01", "inbound text", result)

    md = render_markdown(record)
    for heading in ["## 1. Decision", "## 2. Reasoning", "## 3. Consulted", "## 4. Actions taken", "## 5. Uncertainties", "## 6. What a human still needs to do"]:
        assert heading in md, heading

    with tempfile.TemporaryDirectory() as tmp:
        json_path, md_path = write_record(record, Path(tmp))
        assert json_path.exists() and md_path.exists()
        reloaded = json.loads(json_path.read_text(encoding="utf-8"))
        assert reloaded["case_id"] == "case-01"
        assert md_path.read_text(encoding="utf-8") == md


def test_usage_and_cost_in_record_and_markdown():
    usage = TokenUsage(prompt_tokens=10_000, completion_tokens=2_000, model_calls=5)
    result = AgentResult(decision="done", trace=[], iterations=5, usage=usage)
    record = build("case-04", "inbound", result)

    assert record["usage"]["prompt_tokens"] == 10_000
    assert record["usage"]["completion_tokens"] == 2_000
    assert record["usage"]["total_tokens"] == 12_000
    assert record["usage"]["model_calls"] == 5
    expected_cost = (10_000 / 1_000_000) * INPUT_PRICE + (2_000 / 1_000_000) * OUTPUT_PRICE
    assert abs(record["usage"]["estimated_cost_usd"] - expected_cost) < 1e-9
    assert record["usage"]["pricing"] == {"input_per_1m_usd": INPUT_PRICE, "output_per_1m_usd": OUTPUT_PRICE}

    md = render_markdown(record)
    assert "10,000 in + 2,000 out = 12,000 total across 5 model call(s)" in md


def main():
    tests = [
        test_build_record_modes_and_money,
        test_unresolved_block_flagged_without_escalation,
        test_iteration_cap_marks_escalated,
        test_markdown_and_files_render,
        test_usage_and_cost_in_record_and_markdown,
    ]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} passed")


if __name__ == "__main__":
    main()
