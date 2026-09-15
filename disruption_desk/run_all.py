"""CLI: work every case under cases/ in one sweep, writing output/<case-id>/record.{json,md}
plus a run-level output/summary.{json,md}.

    python -m disruption_desk.run_all
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .agent import Agent
from .config import load_config
from .ops_client import OpsClient
from .record import build_record, write_record

CASES_DIR = Path("cases")
OUTPUT_DIR = Path("output")

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def _case_dirs() -> list[Path]:
    return sorted(p for p in CASES_DIR.iterdir() if p.is_dir() and (p / "inbound.txt").exists())


def _write_summary(rows: list[dict], config, dry_run: bool, output_root: Path) -> tuple[Path, Path]:
    totals = {
        "prompt_tokens": sum(r["prompt_tokens"] for r in rows),
        "completion_tokens": sum(r["completion_tokens"] for r in rows),
        "total_tokens": sum(r["total_tokens"] for r in rows),
        "model_calls": sum(r["model_calls"] for r in rows),
        "estimated_cost_usd": round(sum(r["estimated_cost_usd"] for r in rows), 6),
        "paid_gbp": round(sum(r["paid_gbp"] for r in rows), 2),
        "escalated_count": sum(1 for r in rows if r["escalated"]),
    }
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "model": config.openai_model,
        "pricing": {
            "input_per_1m_usd": config.input_price_per_1m_usd,
            "output_per_1m_usd": config.output_price_per_1m_usd,
        },
        "cases": rows,
        "totals": totals,
    }

    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "summary.json"
    json_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    lines = [
        "# Sweep summary",
        "",
        f"Generated: {summary['generated_at']}",
        f"Mode: {'DRY RUN' if dry_run else 'LIVE'}  |  Model: {config.openai_model}",
        "",
        "| case | escalated | paid £ | tokens in | tokens out | cost $ | decision |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['case_id']} | {'yes' if r['escalated'] else 'no'} | {r['paid_gbp']:.2f} | "
            f"{r['prompt_tokens']:,} | {r['completion_tokens']:,} | {r['estimated_cost_usd']:.4f} | "
            f"{r['headline']} |"
        )
    lines += [
        "",
        f"**Totals** ({totals['escalated_count']}/{len(rows)} escalated): "
        f"£{totals['paid_gbp']:.2f} paid, {totals['prompt_tokens']:,} in + "
        f"{totals['completion_tokens']:,} out = {totals['total_tokens']:,} tokens across "
        f"{totals['model_calls']} model calls, estimated cost **${totals['estimated_cost_usd']:.4f}**.",
        "",
    ]
    md_path = output_root / "summary.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Work every case in cases/ and write a record for each.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Disable dry-run for the whole sweep: actions really fire against the ops API.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show INFO-level logging.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    config = load_config()
    case_dirs = _case_dirs()
    if not case_dirs:
        raise SystemExit(f"No cases found under {CASES_DIR}/")

    rows: list[dict] = []
    print(f"{'case':<10} {'escalated':<10} {'paid_gbp':>10} {'in_tok':>8} {'out_tok':>8} {'cost_usd':>9}  decision")
    for case_dir in case_dirs:
        case_id = case_dir.name
        inbound = (case_dir / "inbound.txt").read_text(encoding="utf-8")

        ops = OpsClient(config, dry_run=not args.live)
        agent = Agent(config, ops)
        result = agent.run(inbound)

        record = build_record(
            case_id, inbound, result, dry_run=ops.dry_run,
            input_price_per_1m_usd=config.input_price_per_1m_usd,
            output_price_per_1m_usd=config.output_price_per_1m_usd,
        )
        write_record(record, OUTPUT_DIR)

        headline = (record["decision"]["summary"] or "").strip().splitlines()
        headline = headline[0][:80] if headline else "(no decision text)"
        money = record["money"]
        paid = money["total_real_paid_gbp"] if args.live else money["total_dry_run_would_pay_gbp"]
        escalated = record["decision"]["escalated"]
        usage = record["usage"]

        rows.append(
            {
                "case_id": case_id,
                "escalated": escalated,
                "paid_gbp": paid,
                "prompt_tokens": usage["prompt_tokens"],
                "completion_tokens": usage["completion_tokens"],
                "total_tokens": usage["total_tokens"],
                "model_calls": usage["model_calls"],
                "estimated_cost_usd": usage["estimated_cost_usd"],
                "headline": headline,
            }
        )
        print(
            f"{case_id:<10} {('yes' if escalated else 'no'):<10} {paid:>10.2f} "
            f"{usage['prompt_tokens']:>8} {usage['completion_tokens']:>8} "
            f"{usage['estimated_cost_usd']:>9.4f}  {headline}"
        )

    json_path, md_path = _write_summary(rows, config, dry_run=not args.live, output_root=OUTPUT_DIR)

    totals_prompt = sum(r["prompt_tokens"] for r in rows)
    totals_completion = sum(r["completion_tokens"] for r in rows)
    totals_cost = sum(r["estimated_cost_usd"] for r in rows)
    print(
        f"\nGrand total: {totals_prompt:,} in + {totals_completion:,} out = "
        f"{totals_prompt + totals_completion:,} tokens, estimated cost ${totals_cost:.4f}"
    )
    print(f"Records written under {OUTPUT_DIR}/, sweep summary at {json_path} and {md_path}")


if __name__ == "__main__":
    main()
