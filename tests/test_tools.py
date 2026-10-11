"""Checks that dispatch() never lets a malformed tool call crash the run.

Run: pytest tests/test_tools.py
"""

from disruption_desk.tools import dispatch


class StubOps:
    """A minimal stand-in for OpsClient - just enough surface to exercise dispatch()."""

    def rebook(self, booking_ref, passenger_ids, option_id, flight_no, date, cabin, fare_gbp, notes=None):
        return {"rebooking_id": "REBK-1", "booking_ref": booking_ref, "fare_gbp": fare_gbp}


def test_missing_required_argument_returns_error_dict_not_raise():
    ops = StubOps()
    result = dispatch(
        ops,
        "rebook",
        {
            "booking_ref": "AER-AAAA",
            "passenger_ids": ["P1"],
            "option_id": "OPT-1",
            "flight_no": "AK1",
            "date": "2026-08-04",
            "cabin": "ECONOMY",
            # fare_gbp deliberately missing - this is the exact crash from the case-02 sweep
        },
    )
    assert isinstance(result, dict)
    assert result["error"] == "invalid_arguments"
    assert result["status_code"] == 400
    assert "fare_gbp" in result["message"]


def test_unexpected_argument_returns_error_dict_not_raise():
    ops = StubOps()
    result = dispatch(
        ops,
        "rebook",
        {
            "booking_ref": "AER-AAAA",
            "passenger_ids": ["P1"],
            "option_id": "OPT-1",
            "flight_no": "AK1",
            "date": "2026-08-04",
            "cabin": "ECONOMY",
            "fare_gbp": 0.0,
            "not_a_real_field": "surprise",
        },
    )
    assert result["error"] == "invalid_arguments"
    assert "not_a_real_field" in result["message"]


def test_unknown_tool_name_returns_error_dict_not_raise():
    ops = StubOps()
    result = dispatch(ops, "definitely_not_a_tool", {})
    assert result["error"] == "unknown_tool"
    assert result["status_code"] == 400


def test_well_formed_call_still_returns_the_real_result():
    ops = StubOps()
    result = dispatch(
        ops,
        "rebook",
        {
            "booking_ref": "AER-AAAA",
            "passenger_ids": ["P1"],
            "option_id": "OPT-1",
            "flight_no": "AK1",
            "date": "2026-08-04",
            "cabin": "ECONOMY",
            "fare_gbp": 0.0,
        },
    )
    assert result == {"rebooking_id": "REBK-1", "booking_ref": "AER-AAAA", "fare_gbp": 0.0}
