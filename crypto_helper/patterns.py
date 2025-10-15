"""Pattern detection utilities."""
from __future__ import annotations

from typing import Iterable, List


def ema_crossover(fast_ema: Iterable[float], slow_ema: Iterable[float]) -> bool:
    fast = list(fast_ema)
    slow = list(slow_ema)
    if len(fast) < 2 or len(slow) < 2:
        return False
    return fast[-2] < slow[-2] and fast[-1] > slow[-1]


def rsi_oversold(rsi_values: Iterable[float], threshold: float = 30) -> bool:
    values = list(rsi_values)
    if not values:
        return False
    return values[-1] < threshold


def bollinger_bounce(close_prices: List[float], lower_band: Iterable[float]) -> bool:
    if len(close_prices) < 2:
        return False
    lb = list(lower_band)
    if not lb:
        return False
    return close_prices[-2] < lb[-1] and close_prices[-1] > lb[-1]
