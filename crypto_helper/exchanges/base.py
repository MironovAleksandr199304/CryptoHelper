"""Base classes and utilities for exchange clients."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Protocol

import requests


@dataclass
class OHLCV:
    """Represents a single OHLCV candle."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleFactory(Protocol):
    """Protocol describing the call signature for candle factories."""

    def __call__(self, raw: List[str]) -> OHLCV:
        ...


class ExchangeClient(ABC):
    """Abstract base client that fetches OHLC data from crypto exchanges."""

    base_url: str

    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()

    @abstractmethod
    def fetch_ohlc(self, symbol: str, interval: str, limit: int = 100) -> List[OHLCV]:
        """Retrieve OHLC data for a symbol.

        Args:
            symbol: Trading pair, e.g. ``BTCUSDT``.
            interval: Exchange-specific candle interval string (e.g. ``1h``).
            limit: Number of candles to return.
        """

    def _request(self, endpoint: str, params: dict[str, str]) -> list:
        """Perform a GET request against the exchange API."""
        response = self.session.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
