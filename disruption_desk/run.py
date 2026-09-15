"""CLI: work one case end to end.

    python -m disruption_desk.run --case cases/case-01
    python -m disruption_desk.run --message path/to/inbound.txt
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .agent import Agent
from .config import load_config
from .ops_client import OpsClient
from .record import build_record, write_record

OUTPUT_DIR = Path("output")

# Model output is arbitrary Unicode; Windows consoles default to cp1252 and crash on it.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def _read_inbound(args: argparse.Namespace) -> tuple[str, str]:
    """Returns (case_id, inbound_text)."""
    if args.case:
        path = Path(args.case) / "inbound.txt"
        case_id = Path(args.case).name
    elif args.message:
        path = Path(args.message)
        case_id = f"adhoc-{path.stem}"
    else:
        raise SystemExit("Provide --case cases/case-NN or --message path/to/file.txt")
    if not path.exists():
        raise SystemExit(f"No such file: {path}")
    return case_id, path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Work one disruption-desk case end to end.")
    parser.add_argument("--case", help="Path to a case directory containing inbound.txt")
    parser.add_argument("--message", help="Path to a raw inbound message file (for a new/unseen case)")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Disable dry-run: rebooking/payment/refund/voucher actions really fire against the ops API.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show INFO-level logging (dry-run lines, retries).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    case_id, inbound = _read_inbound(args)
    config = load_config()
    ops = OpsClient(config, dry_run=not args.live)
    agent = Agent(config, ops)

    result = agent.run(inbound)

    print("=== TOOL CALLS ===")
    if not result.trace:
        print("(none)")
    for i, call in enumerate(result.trace, 1):
        flag = " [BLOCKED]" if call.blocked else ""
        print(f"{i}. {call.name}({call.arguments}){flag}\n   -> {call.result}")

    print("\n=== DECISION ===")
    print(result.decision)
    print(f"\n(iterations={result.iterations}, escalated_by_iteration_cap={result.escalated_by_cap}, dry_run={ops.dry_run})")

    cost = result.usage.estimated_cost_usd(config.input_price_per_1m_usd, config.output_price_per_1m_usd)
    print(
        f"\nTokens: {result.usage.prompt_tokens} in + {result.usage.completion_tokens} out = "
        f"{result.usage.total_tokens} total across {result.usage.model_calls} model call(s)"
    )
    print(f"Estimated cost: ${cost:.4f}")

    record = build_record(
        case_id, inbound, result, dry_run=ops.dry_run,
        input_price_per_1m_usd=config.input_price_per_1m_usd,
        output_price_per_1m_usd=config.output_price_per_1m_usd,
    )
    json_path, md_path = write_record(record, OUTPUT_DIR)
    print(f"\nRecord written to {json_path} and {md_path}")


if __name__ == "__main__":
    main()
