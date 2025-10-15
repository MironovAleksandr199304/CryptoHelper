"""Binance exchange client implementation."""
from __future__ import annotations

from datetime import datetime
from typing import List

from .base import ExchangeClient, OHLCV


class BinanceClient(ExchangeClient):
    base_url = "https://api.binance.com"

    def fetch_ohlc(self, symbol: str, interval: str, limit: int = 100) -> List[OHLCV]:
        params = {"symbol": symbol.upper(), "interval": interval, "limit": str(limit)}
        data = self._request("/api/v3/klines", params=params)
        return [
            OHLCV(
                timestamp=datetime.fromtimestamp(item[0] / 1000),
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                volume=float(item[5]),
            )
            for item in data
        ]
