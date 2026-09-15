# Case record: case-09

Generated: 2026-09-15T11:59:42.460074+00:00
Mode: LIVE
Tokens: 34,635 in + 453 out = 35,088 total across 10 model call(s) - estimated cost $0.0055

## 1. Decision - what the passenger gets

Escalated to a human (queue: OPS_LIAISON).
Summary: Rebooking required for Aisha Bello due to the cancellation of flight AK512. Flight LH520 to Dubai is available for £488.14, which exceeds the per-action autonomy limit.
Requested decision: Please authorize rebooking for passenger Aisha Bello onto flight LH520 for £488.14 following the cancellation of her previous flight.
Agent's recommendation: Issue the ticket for the rebooked flight.
Escalation ID: ESC-00010

Escalated to a human: **yes** (model_escalated)

## 2. Reasoning - what it rests on

- `calculate_entitlements` for `AER-8N4V6J`: status=ASSESSED, policy_version=APCP-2026-04 v11.3
  - Compensation: INSUFFICIENT_DATA (£0.0)
    - S1.3: great-circle distance 5494 km, therefore Band C.
    - S3: operational record shows cause_code=TECHNICAL, which is within Aerlink's control (S3.3).
    - S5.2: arrival delay at final destination is not yet known, because the passenger has not been re-routed. Compensation cannot be assessed until the passenger's re-routing (or refusal) is settled. S10.3 applies.

## 3. Consulted - every read made

**search_bookings**
```json
{
  "arguments": {
    "q": "AER-8N4V6J"
  },
  "result": {
    "query": "AER-8N4V6J",
    "match_count": 1,
    "results": [
      {
        "booking_ref": "AER-8N4V6J",
        "customer_id": "CUS-10010",
        "contact_email": "aisha.bello@mailbox.example",
        "passengers": [
          "Aisha Bello"
        ],
        "segments": [
          "AK512 2026-08-06 LGW-DXB"
        ],
        "matched_on": [
          "booking_reference_exact"
        ]
      }
    ]
  }
}
```

**get_booking**
```json
{
  "arguments": {
    "booking_ref": "AER-8N4V6J"
  },
  "result": {
    "booking_ref": "AER-8N4V6J",
    "customer_id": "CUS-10010",
    "contact_email": "aisha.bello@mailbox.example",
    "contact_phone": "+447700900411",
    "booked_on": "2026-02-09",
    "tier": "GOLD",
    "total_paid_gbp": 812.0,
    "special_requests": "",
    "passengers": [
      {
        "passenger_id": "P1",
        "given_name": "Aisha",
        "surname": "Bello",
        "passenger_type": "ADULT",
        "age": 38,
        "assistance": null,
        "cabin_booked": "ECONOMY",
        "cabin_flown": null
      }
    ],
    "segments": [
      {
        "segment_id": "S1",
        "flight_no": "AK512",
        "date": "2026-08-06",
        "origin": "LGW",
        "destination": "DXB",
        "segment_fare_gbp": 640.0,
        "cabin": "ECONOMY",
        "is_affected": true
      }
    ],
    "final_destination": "DXB",
    "disruption": {
      "affected_segment": "S1",
      "rerouted_onto": null,
      "arrival_delay_minutes": null,
      "informed_days_before": 0
    }
  }
}
```

**get_flight**
```json
{
  "arguments": {
    "flight_no": "AK512",
    "date": "2026-08-06"
  },
  "result": {
    "flight_no": "AK512",
    "date": "2026-08-06",
    "origin": "LGW",
    "destination": "DXB",
    "distance_km": 5494,
    "scheduled_departure": "2026-08-06T21:35:00Z",
    "scheduled_arrival": "2026-08-07T08:20:00Z",
    "status": "CANCELLED",
    "cause_code": "TECHNICAL",
    "cause_note": "Fuel system fault found on turnaround. No spare widebody at LGW. Next Aerlink service DXB 2026-08-07 21:35.",
    "departure_delay_minutes": null,
    "aircraft": "B787-9",
    "operated_by": "Aerlink"
  }
}
```

**calculate_entitlements**
```json
{
  "arguments": {
    "booking_ref": "AER-8N4V6J"
  },
  "result": {
    "booking_ref": "AER-8N4V6J",
    "status": "ASSESSED",
    "authoritative": true,
    "policy_version": "APCP-2026-04 v11.3",
    "note": "S10.2: where this service returns a figure, that figure is the amount owed. It takes precedence over a figure derived by reading the policy text.",
    "journey": {
      "origin": "LGW",
      "final_destination": "DXB",
      "great_circle_distance_km": 5494,
      "band": "C",
      "affected_flight": "AK512:2026-08-06",
      "cause_code": "TECHNICAL",
      "cause_is_extraordinary": false,
      "flight_status": "CANCELLED",
      "departure_delay_minutes": null,
      "arrival_delay_minutes_at_final_destination": null,
      "rerouted_onto": null
    },
    "compensation": {
      "amount_gbp": 0.0,
      "status": "INSUFFICIENT_DATA",
      "reasoning": [
        "S1.3: great-circle distance 5494 km, therefore Band C.",
        "S3: operational record shows cause_code=TECHNICAL, which is within Aerlink's control (S3.3).",
        "S5.2: arrival delay at final destination is not yet known, because the passenger has not been re-routed. Compensation cannot be assessed until the passenger's re-routing (or refusal) is settled. S10.3 applies."
      ]
    },
    "duty_of_care": {
      "triggered": true,
      "basis": "S4.1: flight cancelled, care owed immediately.",
      "note": "S4 care is owed regardless of cause, including extraordinary circumstances (S4.3).",
      "entitlements": [
        {
          "type": "meals_refreshments",
          "cap_gbp": 30.0,
          "per": "passenger per 6 hours"
        },
        {
          "type": "communication",
          "cap": "two calls or equivalent"
        },
        {
          "type": "hotel",
          "cap_gbp": 180.0,
          "per": "room per night",
          "max_nights": 3,
          "note": "Subject to station allocation, S4.5."
        },
        {
          "type": "transport",
          "cap_gbp": 45.0,
          "per": "journey"
        }
      ]
    },
    "passengers": [
      {
        "passenger_id": "P1",
        "name": "Aisha Bello",
        "passenger_type": "ADULT",
        "compensation_gbp": 0.0,
        "compensation_status": "INSUFFICIENT_DATA",
        "downgrade_reimbursement_gbp": 0.0,
        "downgrade_reasoning": [],
        "flags": [],
        "total_payable_gbp": 0.0
      }
    ],
    "total_payable_gbp": 0.0
  }
}
```

**get_hotel_allocation**
```json
{
  "arguments": {
    "iata": "LGW",
    "night": "2026-08-06"
  },
  "result": {
    "station": "LGW",
    "night": "2026-08-06",
    "provider": "Gatwick Airport Lodging Consortium",
    "rooms_total": 40,
    "rooms_remaining": 1,
    "rate_gbp": 165.0
  }
}
```

**search_availability**
```json
{
  "arguments": {
    "origin": "LGW",
    "destination": "DXB",
    "date": "2026-08-07"
  },
  "result": {
    "reason": "service_unavailable",
    "message": "Availability service temporarily unavailable. Retry."
  }
}
```

**search_availability_partners**
```json
{
  "arguments": {
    "origin": "LGW",
    "destination": "DXB",
    "date": "2026-08-07"
  },
  "result": {
    "query": {
      "from": "LGW",
      "to": "DXB",
      "date": "2026-08-07",
      "after": null,
      "booking_ref": null,
      "carrier_scope": "partner"
    },
    "page": 1,
    "page_size": 20,
    "total_results": 8,
    "total_pages": 1,
    "results": [
      {
        "option_id": "OPT-1CCA014224",
        "flight_no": "IB448",
        "operated_by": "Iberia",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "05:35",
        "arrival_local": "14:18",
        "cabin": "ECONOMY",
        "seats_available": 4,
        "fare_gbp": 743.16
      },
      {
        "option_id": "OPT-C2E3294113",
        "flight_no": "IB644",
        "operated_by": "Iberia",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "06:45",
        "arrival_local": "15:49",
        "cabin": "ECONOMY",
        "seats_available": 9,
        "fare_gbp": 736.59
      },
      {
        "option_id": "OPT-64426AA9DA",
        "flight_no": "TP546",
        "operated_by": "TAP Air Portugal",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "07:10",
        "arrival_local": "15:46",
        "cabin": "ECONOMY",
        "seats_available": 0,
        "fare_gbp": 614.99
      },
      {
        "option_id": "OPT-0057194ADF",
        "flight_no": "LH520",
        "operated_by": "Lufthansa",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "11:35",
        "arrival_local": "20:34",
        "cabin": "ECONOMY",
        "seats_available": 1,
        "fare_gbp": 488.14
      },
      {
        "option_id": "OPT-AEF4032924",
        "flight_no": "AF641",
        "operated_by": "Air France",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "12:10",
        "arrival_local": "21:10",
        "cabin": "ECONOMY",
        "seats_available": 7,
        "fare_gbp": 676.88
      },
      {
        "option_id": "OPT-737C37E3B4",
        "flight_no": "TP513",
        "operated_by": "TAP Air Portugal",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "12:40",
        "arrival_local": "21:30",
        "cabin": "ECONOMY",
        "seats_available": 5,
        "fare_gbp": 682.5
      },
      {
        "option_id": "OPT-6E0900DF28",
        "flight_no": "TP573",
        "operated_by": "TAP Air Portugal",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "14:30",
        "arrival_local": "22:59",
        "cabin": "PREMIUM",
        "seats_available": 0,
        "fare_gbp": 297.46
      },
      {
        "option_id": "OPT-551D0BE11D",
        "flight_no": "IB110",
        "operated_by": "Iberia",
        "origin": "LGW",
        "destination": "DXB",
        "date": "2026-08-07",
        "departure_local": "18:20",
        "arrival_local": "03:24+1",
        "cabin": "PREMIUM",
        "seats_available": 2,
        "fare_gbp": 914.65
      }
    ]
  }
}
```

## 4. Actions taken - every write, real or dry-run

### issue_hotel_voucher - `REAL`
**issue_hotel_voucher**
```json
{
  "arguments": {
    "booking_ref": "AER-8N4V6J",
    "station": "LGW",
    "night": "2026-08-06",
    "passenger_ids": [
      "P1"
    ],
    "notes": "Hotel voucher for Aisha Bello due to flight AK512 cancellation."
  },
  "result": {
    "voucher_id": "HTL-00009",
    "issued_at": "2026-09-15T11:59:35Z",
    "status": "ISSUED",
    "station": "LGW",
    "night": "2026-08-06",
    "booking_ref": "AER-8N4V6J",
    "passenger_ids": [
      "P1"
    ],
    "rate_gbp": 165.0,
    "rooms_remaining_after": 0
  }
}
```

### rebook - `BLOCKED`
**rebook**
```json
{
  "arguments": {
    "booking_ref": "AER-8N4V6J",
    "passenger_ids": [
      "P1"
    ],
    "option_id": "OPT-0057194ADF",
    "flight_no": "LH520",
    "date": "2026-08-07",
    "cabin": "ECONOMY",
    "fare_gbp": 488.14,
    "notes": "Rebooked onto Lufthansa flight LH520 due to cancellation of AK512."
  },
  "result": {
    "blocked": true,
    "reason": "\u00a3488.14 exceeds the per-action autonomy limit of \u00a3300.00. Escalate instead."
  }
}
```

### escalate
**escalate**
```json
{
  "arguments": {
    "summary": "Rebooking required for Aisha Bello due to the cancellation of flight AK512. Flight LH520 to Dubai is available for \u00a3488.14, which exceeds the per-action autonomy limit.",
    "requested_decision": "Please authorize rebooking for passenger Aisha Bello onto flight LH520 for \u00a3488.14 following the cancellation of her previous flight.",
    "booking_ref": "AER-8N4V6J",
    "queue": "OPS_LIAISON",
    "recommendation": "Issue the ticket for the rebooked flight."
  },
  "result": {
    "escalation_id": "ESC-00010",
    "raised_at": "2026-09-15T11:59:42Z",
    "status": "OPEN",
    "queue": "OPS_LIAISON",
    "summary": "Rebooking required for Aisha Bello due to the cancellation of flight AK512. Flight LH520 to Dubai is available for \u00a3488.14, which exceeds the per-action autonomy limit.",
    "requested_decision": "Please authorize rebooking for passenger Aisha Bello onto flight LH520 for \u00a3488.14 following the cancellation of her previous flight.",
    "booking_ref": "AER-8N4V6J",
    "recommendation": "Issue the ticket for the rebooked flight.",
    "blocking_clause": null
  }
}
```

Total paid for real: £0.00
Total that would be paid if this were a live run: £0.00

## 5. Uncertainties

- search_availability was unavailable (503): Availability service temporarily unavailable. Retry.
- rebook was blocked by the autonomy guard: £488.14 exceeds the per-action autonomy limit of £300.00. Escalate instead.

## 6. What a human still needs to do

- Escalation raised (`ESC-00010`): Please authorize rebooking for passenger Aisha Bello onto flight LH520 for £488.14 following the cancellation of her previous flight.
  - Queue: OPS_LIAISON
  - Agent's recommendation: Issue the ticket for the rebooked flight.

## Raw tool-call trace (in order)

1. `search_bookings`
2. `get_booking`
3. `get_flight`
4. `calculate_entitlements`
5. `get_hotel_allocation`
6. `issue_hotel_voucher`
7. `search_availability`
8. `search_availability_partners`
9. `rebook` [BLOCKED]
10. `escalate`
