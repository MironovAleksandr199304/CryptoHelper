"""KuCoin exchange client implementation."""
from __future__ import annotations

from datetime import datetime
from typing import List

from .base import ExchangeClient, OHLCV


class KuCoinClient(ExchangeClient):
    base_url = "https://api.kucoin.com"

    def fetch_ohlc(self, symbol: str, interval: str, limit: int = 100) -> List[OHLCV]:
        params = {
            "symbol": symbol.upper(),
            "type": interval,
        }
        data = self._request("/api/v1/market/candles", params=params)
        candles = data.get("data", [])[:limit]
        return [
            OHLCV(
                timestamp=datetime.fromtimestamp(int(item[0])),
                open=float(item[1]),
                close=float(item[2]),
                high=float(item[3]),
                low=float(item[4]),
                volume=float(item[5]),
            )
            for item in candles
        ]
