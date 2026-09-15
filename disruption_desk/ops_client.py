"""Typed client for the Aerlink operations API (env/API.md)."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Optional

import requests

from .config import Config
from .exceptions import (
    OpsAllocationExhaustedError,
    OpsApiError,
    OpsNotFoundError,
    OpsRateLimitedError,
)

logger = logging.getLogger("disruption_desk.ops_client")

_EXCEPTION_BY_STATUS = {
    404: OpsNotFoundError,
    409: OpsAllocationExhaustedError,
}

_MAX_RETRIES = 5
_BACKOFF_BASE_SECONDS = 0.5


@dataclass
class AvailabilityUnavailable:
    """Returned instead of raising when an availability search hits its downstream 503."""

    reason: str = "service_unavailable"
    message: str = "Inventory system did not respond."


class OpsClient:
    def __init__(self, config: Config, dry_run: bool = True, timeout: float = 15.0):
        self._base_url = config.ops_base_url
        self._headers = {"X-Ops-Key": config.ops_api_key}
        self.dry_run = dry_run
        self._timeout = timeout
        self._session = requests.Session()

    # -- internal request plumbing -------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
        treat_503_as_unavailable: bool = False,
    ):
        url = f"{self._base_url}{path}"
        attempt = 0
        while True:
            attempt += 1
            response = self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=self._headers,
                timeout=self._timeout,
            )

            if response.status_code == 429:
                if attempt > _MAX_RETRIES:
                    error, message = self._error_body(response)
                    raise OpsRateLimitedError(429, error, message)
                delay = _BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                logger.warning("429 rate_limited on %s %s, retrying in %.1fs", method, path, delay)
                time.sleep(delay)
                continue

            if response.status_code == 503 and treat_503_as_unavailable:
                _, message = self._error_body(response)
                return AvailabilityUnavailable(message=message or "Inventory system did not respond.")

            if 200 <= response.status_code < 300:
                if response.status_code == 204 or not response.content:
                    return {}
                return response.json()

            error, message = self._error_body(response)
            exc_type = _EXCEPTION_BY_STATUS.get(response.status_code, OpsApiError)
            raise exc_type(response.status_code, error, message)

    @staticmethod
    def _error_body(response: requests.Response) -> tuple[str, str]:
        try:
            body = response.json()
            return body.get("error", "unknown_error"), body.get("message", "")
        except ValueError:
            return "unknown_error", response.text

    def _dry_run_log(self, action: str, **details: Any) -> dict:
        """Fake success for a write method when dry_run is on.

        Shaped like the real endpoint's success response (flat, with the same id field) rather
        than a nested "would_have" preview - the model driving this client needs to read a
        dry-run success as "this action is done", the same way it would read a real one.
        """
        logger.info("DRY-RUN %s %s", action, details)
        result = dict(details)
        result["dry_run"] = True
        result["status"] = "DONE (dry-run: no real money moved or booking changed, but this " \
            "action is complete - do not repeat it)"
        return result

    # -- read endpoints (always execute for real) ------------------------------------

    def health(self) -> dict:
        return self._request("GET", "/health")

    def search_bookings(self, q: str) -> dict:
        return self._request("GET", "/bookings/search", params={"q": q})

    def get_booking(self, booking_ref: str) -> dict:
        return self._request("GET", f"/bookings/{booking_ref}")

    def search_availability(
        self,
        origin: str,
        destination: str,
        date: str,
        after: Optional[str] = None,
        booking_ref: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        params = {
            "from": origin,
            "to": destination,
            "date": date,
            "page": page,
            "page_size": page_size,
        }
        if after:
            params["after"] = after
        if booking_ref:
            params["booking_ref"] = booking_ref
        return self._request(
            "GET", "/flights/availability", params=params, treat_503_as_unavailable=True
        )

    def search_availability_partners(
        self,
        origin: str,
        destination: str,
        date: str,
        after: Optional[str] = None,
        booking_ref: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        params = {
            "from": origin,
            "to": destination,
            "date": date,
            "page": page,
            "page_size": page_size,
        }
        if after:
            params["after"] = after
        if booking_ref:
            params["booking_ref"] = booking_ref
        return self._request(
            "GET",
            "/flights/availability/partners",
            params=params,
            treat_503_as_unavailable=True,
        )

    def get_flight(self, flight_no: str, date: str) -> dict:
        return self._request("GET", f"/flights/{flight_no}", params={"date": date})

    def search_policy(self, q: str, limit: int = 5) -> dict:
        return self._request("GET", "/policy/search", params={"q": q, "limit": limit})

    def get_policy_document(self) -> dict:
        return self._request("GET", "/policy/document")

    def get_customer_history(self, customer_id: str) -> dict:
        return self._request("GET", f"/customers/{customer_id}/history")

    def calculate_entitlements(self, booking_ref: str, passenger_id: Optional[str] = None) -> dict:
        params = {"booking_ref": booking_ref}
        if passenger_id:
            params["passenger_id"] = passenger_id
        return self._request("GET", "/entitlements/calculate", params=params)

    def get_hotel_allocation(self, iata: str, night: str) -> dict:
        return self._request("GET", f"/stations/{iata}/hotel-allocation", params={"night": night})

    def get_disruption_feed(self) -> dict:
        return self._request("GET", "/disruption/feed")

    # -- write endpoints (gated by dry_run; genuinely move money) --------------------

    def rebook(
        self,
        booking_ref: str,
        passenger_ids: list[str],
        option_id: str,
        flight_no: str,
        date: str,
        cabin: str,
        fare_gbp: float,
        notes: Optional[str] = None,
    ):
        body = {
            "booking_ref": booking_ref,
            "passenger_ids": passenger_ids,
            "option_id": option_id,
            "flight_no": flight_no,
            "date": date,
            "cabin": cabin,
            "fare_gbp": fare_gbp,
            "notes": notes,
        }
        if self.dry_run:
            return self._dry_run_log(
                "rebook",
                **body,
                rebooking_id=f"DRYRUN-REBK-{uuid.uuid4().hex[:8].upper()}",
            )
        return self._request("POST", "/rebooking", json_body=body)

    def cancel_rebooking(self, rebooking_id: str):
        if self.dry_run:
            return self._dry_run_log(
                "cancel_rebooking",
                rebooking_id=rebooking_id,
                cancellation_fee_gbp=65.0,
            )
        return self._request("POST", f"/rebooking/{rebooking_id}/cancel")

    def issue_hotel_voucher(
        self,
        booking_ref: str,
        station: str,
        night: str,
        passenger_ids: list[str],
        notes: Optional[str] = None,
    ):
        body = {
            "booking_ref": booking_ref,
            "station": station,
            "night": night,
            "passenger_ids": passenger_ids,
            "notes": notes,
        }
        if self.dry_run:
            return self._dry_run_log(
                "issue_hotel_voucher",
                **body,
                voucher_id=f"DRYRUN-VCHR-{uuid.uuid4().hex[:8].upper()}",
            )
        return self._request("POST", "/vouchers/hotel", json_body=body)

    def pay_compensation(
        self,
        booking_ref: str,
        amount_gbp: float,
        passenger_ids: list[str],
        reason: Optional[str] = None,
    ):
        body = {
            "booking_ref": booking_ref,
            "amount_gbp": amount_gbp,
            "passenger_ids": passenger_ids,
            "reason": reason,
        }
        if self.dry_run:
            return self._dry_run_log(
                "pay_compensation",
                **body,
                payment_id=f"DRYRUN-PAY-{uuid.uuid4().hex[:8].upper()}",
            )
        return self._request("POST", "/payments/compensation", json_body=body)

    def pay_goodwill(self, booking_ref: str, amount_gbp: float, reason: str):
        body = {"booking_ref": booking_ref, "amount_gbp": amount_gbp, "reason": reason}
        if self.dry_run:
            return self._dry_run_log(
                "pay_goodwill",
                **body,
                payment_id=f"DRYRUN-PAY-{uuid.uuid4().hex[:8].upper()}",
            )
        return self._request("POST", "/payments/goodwill", json_body=body)

    def refund(
        self,
        booking_ref: str,
        amount_gbp: float,
        passenger_ids: Optional[list[str]] = None,
        reason: Optional[str] = None,
    ):
        body = {
            "booking_ref": booking_ref,
            "amount_gbp": amount_gbp,
            "passenger_ids": passenger_ids,
            "reason": reason,
        }
        if self.dry_run:
            return self._dry_run_log(
                "refund",
                **body,
                refund_id=f"DRYRUN-RFND-{uuid.uuid4().hex[:8].upper()}",
            )
        return self._request("POST", "/refunds", json_body=body)

    # -- non-financial write, admin, misc --------------------------------------------

    def escalate(
        self,
        summary: str,
        requested_decision: str,
        booking_ref: Optional[str] = None,
        queue: Optional[str] = None,
        recommendation: Optional[str] = None,
        blocking_clause: Optional[str] = None,
    ) -> dict:
        body = {
            "summary": summary,
            "requested_decision": requested_decision,
            "booking_ref": booking_ref,
            "queue": queue,
            "recommendation": recommendation,
            "blocking_clause": blocking_clause,
        }
        return self._request("POST", "/escalations", json_body=body)

    def audit(self) -> dict:
        return self._request("GET", "/_audit")

    def reset(self) -> dict:
        return self._request("POST", "/_reset")
