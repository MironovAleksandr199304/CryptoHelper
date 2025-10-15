"""Minimal stub mimicking the parts of ``requests`` used in tests."""
from __future__ import annotations

from dataclasses import dataclass


class RequestException(Exception):
    """Base exception used to mimic ``requests`` error hierarchy."""


class HTTPError(RequestException):
    """HTTP error placeholder matching requests.HTTPError."""


@dataclass
class Response:
    status_code: int = 200
    payload: dict | None = None
    text: str = ""

    def json(self) -> dict:
        if self.payload is None:
            return {}
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(f"HTTP {self.status_code}: {self.text}")


class Session:
    """Very small stand-in for :class:`requests.Session`."""

    def get(self, url: str, params: dict | None = None, timeout: float | None = None):
        raise RequestException("HTTP requests are unavailable in the test environment")

    def post(self, url: str, json: dict | None = None, timeout: float | None = None):
        raise RequestException("HTTP requests are unavailable in the test environment")


__all__ = [
    "HTTPError",
    "RequestException",
    "Response",
    "Session",
]
