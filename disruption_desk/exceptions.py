"""Typed exceptions for the operations API client."""

from __future__ import annotations


class OpsApiError(Exception):
    """Base error for any non-2xx response from the ops API."""

    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(f"[{status_code} {error}] {message}")


class OpsNotFoundError(OpsApiError):
    """404 - the addressed record does not exist."""


class OpsAllocationExhaustedError(OpsApiError):
    """409 - the requested resource (e.g. hotel room) is no longer available."""


class OpsRateLimitedError(OpsApiError):
    """429 - rate limit exceeded and retries were exhausted."""
