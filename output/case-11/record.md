# Case record: case-11

Generated: 2026-09-15T12:00:11.617934+00:00
Mode: LIVE
Tokens: 28,806 in + 423 out = 29,229 total across 8 model call(s) - estimated cost $0.0046

## 1. Decision - what the passenger gets

Escalated to a human (queue: GENERAL).
Summary: Passenger Kenneth Braithwaite (AER-7P4R2M) has a cancelled flight AK150 due to a technical fault. He needs a hotel room and a rebooking to Rome on EI857 for a cost of £316.54, which exceeds my approval limit.
Requested decision: Please approve duty-of-care arrangements for a hotel and authorize the rebooking to EI857 on 07 Aug 2026 for Kenneth Braithwaite.
Escalation ID: ESC-00012

Escalated to a human: **yes** (model_escalated)

## 2. Reasoning - what it rests on

- `calculate_entitlements` for `AER-7P4R2M`: status=ASSESSED, policy_version=APCP-2026-04 v11.3
  - Compensation: INSUFFICIENT_DATA (£0.0)
    - S1.3: great-circle distance 1435 km, therefore Band A.
    - S3: operational record shows cause_code=TECHNICAL, which is within Aerlink's control (S3.3).
    - S5.2: arrival delay at final destination is not yet known, because the passenger has not been re-routed. Compensation cannot be assessed until the passenger's re-routing (or refusal) is settled. S10.3 applies.

## 3. Consulted - every read made

**search_bookings**
```json
{
  "arguments": {
    "q": "AER-7P4R2M"
  },
  "result": {
    "query": "AER-7P4R2M",
    "match_count": 1,
    "results": [
      {
        "booking_ref": "AER-7P4R2M",
        "customer_id": "CUS-10012",
        "contact_email": "k.braithwaite@mailbox.example",
        "passengers": [
          "Kenneth Braithwaite"
        ],
        "segments": [
          "AK150 2026-08-06 LGW-FCO"
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
    "booking_ref": "AER-7P4R2M"
  },
  "result": {
    "booking_ref": "AER-7P4R2M",
    "customer_id": "CUS-10012",
    "contact_email": "k.braithwaite@mailbox.example",
    "contact_phone": "+447700900433",
    "booked_on": "2026-07-21",
    "tier": "NONE",
    "total_paid_gbp": 267.0,
    "special_requests": "",
    "passengers": [
      {
        "passenger_id": "P1",
        "given_name": "Kenneth",
        "surname": "Braithwaite",
        "passenger_type": "ADULT",
        "age": 66,
        "assistance": null,
        "cabin_booked": "ECONOMY",
        "cabin_flown": null
      }
    ],
    "segments": [
      {
        "segment_id": "S1",
        "flight_no": "AK150",
        "date": "2026-08-06",
        "origin": "LGW",
        "destination": "FCO",
        "segment_fare_gbp": 199.0,
        "cabin": "ECONOMY",
        "is_affected": true
      }
    ],
    "final_destination": "FCO",
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
    "flight_no": "AK150",
    "date": "2026-08-06"
  },
  "result": {
    "flight_no": "AK150",
    "date": "2026-08-06",
    "origin": "LGW",
    "destination": "FCO",
    "distance_km": 1435,
    "scheduled_departure": "2026-08-06T19:50:00Z",
    "scheduled_arrival": "2026-08-06T23:15:00Z",
    "status": "CANCELLED",
    "cause_code": "TECHNICAL",
    "cause_note": "Nosewheel steering fault. Aircraft withdrawn. No further FCO service this date.",
    "departure_delay_minutes": null,
    "aircraft": "A320",
    "operated_by": "Aerlink"
  }
}
```

**calculate_entitlements**
```json
{
  "arguments": {
    "booking_ref": "AER-7P4R2M",
    "passenger_id": "P1"
  },
  "result": {
    "booking_ref": "AER-7P4R2M",
    "status": "ASSESSED",
    "authoritative": true,
    "policy_version": "APCP-2026-04 v11.3",
    "note": "S10.2: where this service returns a figure, that figure is the amount owed. It takes precedence over a figure derived by reading the policy text.",
    "journey": {
      "origin": "LGW",
      "final_destination": "FCO",
      "great_circle_distance_km": 1435,
      "band": "A",
      "affected_flight": "AK150:2026-08-06",
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
        "S1.3: great-circle distance 1435 km, therefore Band A.",
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
        "name": "Kenneth Braithwaite",
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

**search_availability**
```json
{
  "arguments": {
    "origin": "LGW",
    "destination": "FCO",
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
    "destination": "FCO",
    "date": "2026-08-07"
  },
  "result": {
    "query": {
      "from": "LGW",
      "to": "FCO",
      "date": "2026-08-07",
      "after": null,
      "booking_ref": null,
      "carrier_scope": "partner"
    },
    "page": 1,
    "page_size": 20,
    "total_results": 13,
    "total_pages": 1,
    "results": [
      {
        "option_id": "OPT-CC948688EA",
        "flight_no": "EI388",
        "operated_by": "Aer Lingus",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "05:45",
        "arrival_local": "08:32",
        "cabin": "ECONOMY",
        "seats_available": 1,
        "fare_gbp": 273.4
      },
      {
        "option_id": "OPT-2B5F811E2C",
        "flight_no": "EI682",
        "operated_by": "Aer Lingus",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "05:45",
        "arrival_local": "08:09",
        "cabin": "ECONOMY",
        "seats_available": 1,
        "fare_gbp": 572.22
      },
      {
        "option_id": "OPT-4909D63202",
        "flight_no": "AF285",
        "operated_by": "Air France",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "08:25",
        "arrival_local": "10:56",
        "cabin": "ECONOMY",
        "seats_available": 6,
        "fare_gbp": 875.85
      },
      {
        "option_id": "OPT-40EA2190E1",
        "flight_no": "TP215",
        "operated_by": "TAP Air Portugal",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "10:35",
        "arrival_local": "13:14",
        "cabin": "ECONOMY",
        "seats_available": 7,
        "fare_gbp": 318.61
      },
      {
        "option_id": "OPT-C1F40298C3",
        "flight_no": "IB658",
        "operated_by": "Iberia",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "10:45",
        "arrival_local": "13:08",
        "cabin": "ECONOMY",
        "seats_available": 8,
        "fare_gbp": 423.4
      },
      {
        "option_id": "OPT-EBEEE0BBB9",
        "flight_no": "LH436",
        "operated_by": "Lufthansa",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "14:05",
        "arrival_local": "16:39",
        "cabin": "ECONOMY",
        "seats_available": 8,
        "fare_gbp": 363.83
      },
      {
        "option_id": "OPT-F6A8425E71",
        "flight_no": "KL793",
        "operated_by": "KLM",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "16:05",
        "arrival_local": "18:40",
        "cabin": "ECONOMY",
        "seats_available": 1,
        "fare_gbp": 544.24
      },
      {
        "option_id": "OPT-D4A0DC0D76",
        "flight_no": "LH248",
        "operated_by": "Lufthansa",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "17:25",
        "arrival_local": "19:47",
        "cabin": "ECONOMY",
        "seats_available": 4,
        "fare_gbp": 542.4
      },
      {
        "option_id": "OPT-27160E1C5F",
        "flight_no": "EI762",
        "operated_by": "Aer Lingus",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "18:50",
        "arrival_local": "21:44",
        "cabin": "ECONOMY",
        "seats_available": 6,
        "fare_gbp": 476.07
      },
      {
        "option_id": "OPT-7E345F2DB3",
        "flight_no": "EI857",
        "operated_by": "Aer Lingus",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "18:55",
        "arrival_local": "21:45",
        "cabin": "ECONOMY",
        "seats_available": 2,
        "fare_gbp": 316.54
      },
      {
        "option_id": "OPT-45120A538E",
        "flight_no": "KL529",
        "operated_by": "KLM",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "19:10",
        "arrival_local": "22:03",
        "cabin": "ECONOMY",
        "seats_available": 4,
        "fare_gbp": 535.64
      },
      {
        "option_id": "OPT-FACF5E3A66",
        "flight_no": "LH549",
        "operated_by": "Lufthansa",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "19:45",
        "arrival_local": "22:26",
        "cabin": "BUSINESS",
        "seats_available": 1,
        "fare_gbp": 895.8
      },
      {
        "option_id": "OPT-204AA5D168",
        "flight_no": "AF938",
        "operated_by": "Air France",
        "origin": "LGW",
        "destination": "FCO",
        "date": "2026-08-07",
        "departure_local": "21:45",
        "arrival_local": "00:33+1",
        "cabin": "BUSINESS",
        "seats_available": 2,
        "fare_gbp": 683.2
      }
    ]
  }
}
```

## 4. Actions taken - every write, real or dry-run

### issue_hotel_voucher - `FAILED`
**issue_hotel_voucher**
```json
{
  "arguments": {
    "booking_ref": "AER-7P4R2M",
    "station": "LGW",
    "night": "2026-08-06",
    "passenger_ids": [
      "P1"
    ]
  },
  "result": {
    "error": "allocation_exhausted",
    "message": "No rooms remain in the Aerlink allocation at LGW for 2026-08-06.",
    "status_code": 409
  }
}
```

### rebook - `BLOCKED`
**rebook**
```json
{
  "arguments": {
    "booking_ref": "AER-7P4R2M",
    "passenger_ids": [
      "P1"
    ],
    "option_id": "OPT-7E345F2DB3",
    "flight_no": "EI857",
    "date": "2026-08-07",
    "cabin": "ECONOMY",
    "fare_gbp": 316.54
  },
  "result": {
    "blocked": true,
    "reason": "\u00a3316.54 exceeds the per-action autonomy limit of \u00a3300.00. Escalate instead."
  }
}
```

### escalate
**escalate**
```json
{
  "arguments": {
    "summary": "Passenger Kenneth Braithwaite (AER-7P4R2M) has a cancelled flight AK150 due to a technical fault. He needs a hotel room and a rebooking to Rome on EI857 for a cost of \u00a3316.54, which exceeds my approval limit.",
    "requested_decision": "Please approve duty-of-care arrangements for a hotel and authorize the rebooking to EI857 on 07 Aug 2026 for Kenneth Braithwaite.",
    "booking_ref": "AER-7P4R2M"
  },
  "result": {
    "escalation_id": "ESC-00012",
    "raised_at": "2026-09-15T12:00:11Z",
    "status": "OPEN",
    "queue": null,
    "summary": "Passenger Kenneth Braithwaite (AER-7P4R2M) has a cancelled flight AK150 due to a technical fault. He needs a hotel room and a rebooking to Rome on EI857 for a cost of \u00a3316.54, which exceeds my approval limit.",
    "requested_decision": "Please approve duty-of-care arrangements for a hotel and authorize the rebooking to EI857 on 07 Aug 2026 for Kenneth Braithwaite.",
    "booking_ref": "AER-7P4R2M",
    "recommendation": null,
    "blocking_clause": null
  }
}
```

Total paid for real: £0.00
Total that would be paid if this were a live run: £0.00

## 5. Uncertainties

- search_availability was unavailable (503): Availability service temporarily unavailable. Retry.
- issue_hotel_voucher failed: allocation_exhausted - No rooms remain in the Aerlink allocation at LGW for 2026-08-06.
- rebook was blocked by the autonomy guard: £316.54 exceeds the per-action autonomy limit of £300.00. Escalate instead.

## 6. What a human still needs to do

- Escalation raised (`ESC-00012`): Please approve duty-of-care arrangements for a hotel and authorize the rebooking to EI857 on 07 Aug 2026 for Kenneth Braithwaite.

## Raw tool-call trace (in order)

1. `search_bookings`
2. `get_booking`
3. `get_flight`
4. `calculate_entitlements`
5. `search_availability`
6. `search_availability_partners`
7. `issue_hotel_voucher`
8. `rebook` [BLOCKED]
9. `escalate`
