# Aerlink Disruption Desk

An OpenAI tool-calling agent that works an airline disruption case end to end: reads an inbound
passenger message, establishes who's writing and what actually happened from Aerlink's own
records, works out what's owed versus what's asked, then either acts (rebooking, hotel voucher,
duty-of-care payment) or escalates to a human — producing a `record.json` + `record.md` for every
case it handles.

The reasoning behind what it does and doesn't do — approach, assumptions, prompting, cost,
failure handling, and known limitations — is in [`DECISIONS.md`](DECISIONS.md).

## Prerequisites

- Python 3 (developed against 3.13).
- Two keys in `.env`: `OPS_API_KEY` (the default in `.env.example` already matches the local ops
  server, included for local dev — change it if you run the ops server with a different key) and
  `OPENAI_API_KEY` (your own OpenAI API key).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # fill in OPENAI_API_KEY
```

## Run everything — the one command

```bash
python env/ops_server.py          # terminal 1 — the local ops API
python -m disruption_desk.run_all # terminal 2 — works all twelve cases in cases/
```

This writes `output/<case-id>/record.json` and `record.md` for every case, plus a run-level
`output/summary.json` / `summary.md` (per-case and total: money paid, tokens, estimated cost,
escalation count). **Dry-run is the default** — no real rebooking, payment, refund, or voucher
ever fires unless you pass `--live` (below).

## Run a single case

```bash
python -m disruption_desk.run --case cases/case-01
```

## Run a new, unseen case

```bash
python -m disruption_desk.run --message path/to/inbound.txt
```

Point it at any raw inbound message file — this is the documented entry point for a new case.

## Run for real

Both `run` and `run_all` default to dry-run (nothing real happens; write actions are logged and a
realistic fake success is returned). Add `--live` to actually fire rebookings, payments, refunds,
and vouchers against the ops API:

```bash
python -m disruption_desk.run_all --live
```

Add `-v` to either command for INFO-level logging (dry-run lines, 429 retries).

## Where output lands

- `output/<case-id>/record.json` — machine-readable: decision, reasoning, every read consulted,
  every write action taken (and whether it was real/dry-run/blocked/failed), uncertainties, human
  follow-up, token usage and estimated cost, and the full raw tool-call trace.
- `output/<case-id>/record.md` — the same record, human-readable.
- `output/summary.json` / `output/summary.md` — written only by `run_all`: one row per case plus
  grand totals.

## Tests

No network or API key needed — the OpenAI client and the ops API client are both faked:

```bash
python tests/test_agent.py    # the tool-call loop and every code-enforced guardrail
python tests/test_record.py   # record.json/record.md construction from a trace
python tests/test_tools.py    # dispatch() never lets a malformed tool call crash the run
```

To check the ops-API client layer for real (starts nothing else, just needs the server running):

```bash
python env/ops_server.py
python scripts/smoke_test.py
```
