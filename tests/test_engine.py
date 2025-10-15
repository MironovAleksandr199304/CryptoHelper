"""Unit tests for the signal engine behaviour."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
import unittest

from crypto_helper._compat import requests

from crypto_helper.engine import SignalConfig, SignalEngine
from crypto_helper.exchanges.base import ExchangeClient, OHLCV


class DummyExchange(ExchangeClient):
    """Exchange stub that records requested candle limits."""

    base_url = "https://example.com"

    def __init__(self, candles: List[OHLCV]):
        super().__init__()
        self._candles = candles
        self.last_limit: int | None = None

    def fetch_ohlc(self, symbol: str, interval: str, limit: int = 100) -> List[OHLCV]:
        self.last_limit = limit
        return self._candles[-limit:]


class DummyNotifier:
    """Telegram notifier stub used for capturing outgoing messages."""

    def __init__(self, *, raise_error: bool = False, return_false: bool = False):
        self.raise_error = raise_error
        self.return_false = return_false
        self.messages: List[str] = []

    def send_message(self, text: str) -> bool:
        self.messages.append(text)
        if self.raise_error:
            raise requests.RequestException("network failure")
        if self.return_false:
            return False
        return True


def _make_candles(count: int) -> List[OHLCV]:
    base = datetime(2024, 1, 1)
    candles = []
    price = 100.0
    for index in range(count):
        timestamp = base + timedelta(minutes=index)
        price += 0.5  # simple uptrend keeps indicator logic stable
        candles.append(
            OHLCV(
                timestamp=timestamp,
                open=price - 0.3,
                high=price + 0.3,
                low=price - 0.6,
                close=price,
                volume=1000 + index,
            )
        )
    return candles


class SignalEngineTests(unittest.TestCase):
    def test_engine_requests_sufficient_candles(self) -> None:
        candles = _make_candles(400)
        exchange = DummyExchange(candles)
        notifier = DummyNotifier()
        config = SignalConfig(
            symbol="BTCUSDT",
            interval="1h",
            exchange=exchange,
            telegram_notifier=notifier,
        )
        engine = SignalEngine()
        expected_limit = engine._required_candles(config)

        signals = engine.run(config)

        self.assertEqual(exchange.last_limit, expected_limit)
        self.assertIn("summary", signals)
        self.assertTrue(notifier.messages, "Notification message should be generated")

    def test_engine_handles_notifier_errors_gracefully(self) -> None:
        candles = _make_candles(400)
        exchange = DummyExchange(candles)
        notifier = DummyNotifier(raise_error=True)
        config = SignalConfig(
            symbol="ETHUSDT",
            interval="4h",
            exchange=exchange,
            telegram_notifier=notifier,
        )
        engine = SignalEngine()

        # Should not raise even if the notifier fails internally
        engine.run(config)

        self.assertTrue(notifier.messages, "Engine must attempt to send a Telegram message")


if __name__ == "__main__":
    unittest.main()
