"""Indicator calculations for the CryptoHelper engine."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import List


@dataclass
class IndicatorResult:
    name: str
    values: List[float]


def ema(prices: Sequence[float], period: int) -> List[float]:
    if period <= 0:
        raise ValueError("EMA period must be positive")
    if len(prices) < period:
        raise ValueError("Not enough price data for EMA")

    multiplier = 2 / (period + 1)
    ema_values: List[float] = []
    sma = sum(prices[:period]) / period
    ema_values.append(sma)
    for price in prices[period:]:
        sma = (price - sma) * multiplier + sma
        ema_values.append(sma)
    return ema_values


def rsi(prices: Sequence[float], period: int = 14) -> List[float]:
    if period <= 0:
        raise ValueError("RSI period must be positive")
    if len(prices) <= period:
        raise ValueError("Not enough price data for RSI")

    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rs_values = []
    rsi_values = []

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rs = float("inf")
        else:
            rs = avg_gain / avg_loss
        rs_values.append(rs)
        rsi_values.append(100 - (100 / (1 + rs)))

    return rsi_values


def macd(prices: Sequence[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> tuple[List[float], List[float], List[float]]:
    if slow_period <= fast_period:
        raise ValueError("Slow period must be greater than fast period")
    if len(prices) <= slow_period:
        raise ValueError("Not enough price data for MACD")

    fast_ema = ema(prices, fast_period)
    slow_ema = ema(prices, slow_period)
    macd_line = [f - s for f, s in zip(fast_ema[-len(slow_ema):], slow_ema)]
    signal_line = ema(macd_line, signal_period)
    histogram = [m - s for m, s in zip(macd_line[-len(signal_line):], signal_line)]
    return macd_line, signal_line, histogram


def bollinger_bands(prices: Sequence[float], period: int = 20, num_std_dev: float = 2.0) -> tuple[List[float], List[float], List[float]]:
    if period <= 0:
        raise ValueError("Period must be positive")
    if len(prices) < period:
        raise ValueError("Not enough price data for Bollinger Bands")

    mid_band = []
    upper_band = []
    lower_band = []

    for i in range(len(prices) - period + 1):
        window = prices[i : i + period]
        mean = sum(window) / period
        variance = sum((price - mean) ** 2 for price in window) / period
        std_dev = variance ** 0.5
        mid_band.append(mean)
        upper_band.append(mean + num_std_dev * std_dev)
        lower_band.append(mean - num_std_dev * std_dev)

    return upper_band, mid_band, lower_band
