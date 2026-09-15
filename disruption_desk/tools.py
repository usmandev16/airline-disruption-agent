"""Maps OpsClient read/write methods onto OpenAI tool schemas."""

from __future__ import annotations

from typing import Any

from .ops_client import OpsClient

# Tool names that spend money or change a passenger's journey.
WRITE_TOOLS = {
    "rebook",
    "pay_compensation",
    "pay_goodwill",
    "refund",
    "issue_hotel_voucher",
    "escalate",
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_bookings",
            "description": "Search bookings by reference, email, phone, or passenger name/surname. "
            "Not fuzzy but not strict - a surname can match several bookings, check match_count.",
            "parameters": {
                "type": "object",
                "properties": {"q": {"type": "string"}},
                "required": ["q"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_booking",
            "description": "Fetch the full booking record: passengers, segments, disruption block, "
            "fare, special requests.",
            "parameters": {
                "type": "object",
                "properties": {"booking_ref": {"type": "string"}},
                "required": ["booking_ref"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight",
            "description": "The operational record (status, cause_code, delays) for one flight on "
            "one date. This is Aerlink's own record of what happened - trust this over the "
            "passenger's account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_no": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["flight_no", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_entitlements",
            "description": "Authoritative compensation and duty-of-care calculation for a booking. "
            "Its figures take precedence over your own reading of the policy text (policy S10.2). "
            "Always call this before deciding what a passenger is owed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_ref": {"type": "string"},
                    "passenger_id": {"type": "string", "description": "Optional, restrict to one passenger."},
                },
                "required": ["booking_ref"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_availability",
            "description": "Search Aerlink's own seat inventory for a re-routing option. Can return "
            "'unavailable' when the downstream inventory system is down (by design, intermittently) "
            "- treat that as no answer yet, not as no seats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "IATA code"},
                    "destination": {"type": "string", "description": "IATA code"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "after": {"type": "string", "description": "Optional HH:MM, only later departures"},
                    "booking_ref": {"type": "string", "description": "Optional, adds arrival delay vs original"},
                },
                "required": ["origin", "destination", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_availability_partners",
            "description": "Same as search_availability but against partner-carrier inventory. "
            "fare_gbp on results is a real cost, not usually zero.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "IATA code"},
                    "destination": {"type": "string", "description": "IATA code"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "after": {"type": "string", "description": "Optional HH:MM, only later departures"},
                    "booking_ref": {"type": "string", "description": "Optional, adds arrival delay vs original"},
                },
                "required": ["origin", "destination", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_history",
            "description": "The customer's record and past cases - useful for context, e.g. repeat "
            "issues or flags.",
            "parameters": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hotel_allocation",
            "description": "Rooms remaining in Aerlink's contracted hotel allocation at a station "
            "for one night. Check before issuing a hotel voucher.",
            "parameters": {
                "type": "object",
                "properties": {
                    "iata": {"type": "string"},
                    "night": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["iata", "night"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Keyword search over the Passenger Care Policy, for procedural questions "
            "(e.g. what evidence is needed, escalation rules). Do not use this to re-derive "
            "compensation or duty-of-care figures - calculate_entitlements is authoritative for those.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["q"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rebook",
            "description": "Confirm seats and issue a new itinerary. Genuinely changes the "
            "passenger's journey. Use an option_id from a search_availability(_partners) call you "
            "actually made - never invent one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_ref": {"type": "string"},
                    "passenger_ids": {"type": "array", "items": {"type": "string"}},
                    "option_id": {"type": "string"},
                    "flight_no": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "cabin": {"type": "string"},
                    "fare_gbp": {"type": "number", "description": "Additional fare payable, from the availability result."},
                    "notes": {"type": "string"},
                },
                "required": ["booking_ref", "passenger_ids", "option_id", "flight_no", "date", "cabin", "fare_gbp"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pay_compensation",
            "description": "Pay statutory compensation. This always requires human sign-off first - "
            "do not call this yourself; call escalate instead with the entitlements figure and let "
            "a human authorise the payment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_ref": {"type": "string"},
                    "amount_gbp": {"type": "number"},
                    "passenger_ids": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string"},
                },
                "required": ["booking_ref", "amount_gbp", "passenger_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pay_goodwill",
            "description": "Pay a discretionary goodwill amount, e.g. reimbursing a passenger's "
            "actual duty-of-care spend (meals, transport) up to the policy cap. Genuinely spends money.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_ref": {"type": "string"},
                    "amount_gbp": {"type": "number"},
                    "reason": {"type": "string", "description": "Required: what this reimburses and why."},
                },
                "required": ["booking_ref", "amount_gbp", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "refund",
            "description": "Refund all or part of a booking. Genuinely spends money.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_ref": {"type": "string"},
                    "amount_gbp": {"type": "number"},
                    "passenger_ids": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string"},
                },
                "required": ["booking_ref", "amount_gbp"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_hotel_voucher",
            "description": "Issue a hotel voucher against the station's contracted allocation for "
            "one night. Genuinely spends money. Check get_hotel_allocation first if you need to know "
            "rooms remain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_ref": {"type": "string"},
                    "station": {"type": "string", "description": "IATA code"},
                    "night": {"type": "string", "description": "YYYY-MM-DD"},
                    "passenger_ids": {"type": "array", "items": {"type": "string"}},
                    "notes": {"type": "string"},
                },
                "required": ["booking_ref", "station", "night", "passenger_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate",
            "description": "Hand the case to a human team instead of acting yourself. Use this "
            "whenever you are not confident enough to act autonomously: ambiguous identity, "
            "statutory compensation payable, insufficient data, or anything above your autonomy limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "requested_decision": {"type": "string", "description": "What you need the human to decide."},
                    "booking_ref": {"type": "string"},
                    "queue": {
                        "type": "string",
                        "enum": ["SUPERVISOR", "YTP", "SPECIAL_ASSISTANCE", "OPS_LIAISON", "CUSTOMER_CONDUCT", "LOST_PROPERTY", "GENERAL"],
                    },
                    "recommendation": {"type": "string"},
                    "blocking_clause": {"type": "string"},
                },
                "required": ["summary", "requested_decision"],
            },
        },
    },
]


def dispatch(ops: OpsClient, name: str, arguments: dict) -> Any:
    """Call the OpsClient method matching a tool name.

    A malformed call from the model (missing/extra/wrong-type arguments) must never crash the
    run - it comes back as a normal error result instead, so the model can see what it did
    wrong and correct it on the next turn.
    """
    method = getattr(ops, name, None)
    if method is None:
        return {"error": "unknown_tool", "message": f"Unknown tool: {name}", "status_code": 400}
    try:
        return method(**arguments)
    except TypeError as exc:
        return {"error": "invalid_arguments", "message": f"{name}: {exc}", "status_code": 400}
