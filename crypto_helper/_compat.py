"""Compatibility helpers for optional third-party dependencies."""
from __future__ import annotations

try:  # pragma: no cover - executed depending on environment
    import requests as _requests  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for offline tests
    from . import _requests_stub as _requests

requests = _requests

__all__ = ["requests"]
