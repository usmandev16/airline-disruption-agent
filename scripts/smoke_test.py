"""Sanity check that the ops client works against the running server.

Run: python scripts/smoke_test.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from disruption_desk import OpsClient, load_config

BOOKING_REF = "AER-4K2P9X"


def show(title: str, payload) -> None:
    print(f"\n--- {title} ---")
    print(json.dumps(payload, indent=2, default=str))


def main() -> None:
    config = load_config()
    client = OpsClient(config, dry_run=True)

    show("health", client.health())

    search = client.search_bookings(BOOKING_REF)
    show("search_bookings", search)

    booking = client.get_booking(BOOKING_REF)
    show("get_booking", booking)

    segment = booking["segments"][0]
    flight = client.get_flight(segment["flight_no"], segment["date"])
    show("get_flight", flight)

    entitlements = client.calculate_entitlements(BOOKING_REF)
    show("calculate_entitlements", entitlements)

    print("\nSmoke test passed.")


if __name__ == "__main__":
    main()
