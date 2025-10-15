"""Crypto signal engine that fetches data, computes indicators, and sends alerts."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Protocol

from .exchanges.base import ExchangeClient, OHLCV
from .indicators import core as indicators
from .notifications.telegram import TelegramNotifier
from . import patterns

logger = logging.getLogger(__name__)


class SignalFormatter(Protocol):
    def __call__(self, symbol: str, signals: Dict[str, str]) -> str:
        ...


@dataclass
class SignalConfig:
    symbol: str
    interval: str
    exchange: ExchangeClient
    telegram_notifier: TelegramNotifier
    ema_fast: int = 50
    ema_slow: int = 200
    rsi_period: int = 14
    bollinger_period: int = 20
    bollinger_std_dev: float = 2.0


class SignalEngine:
    def __init__(self, formatter: SignalFormatter | None = None) -> None:
        self.formatter = formatter or self.default_formatter

    def run(self, config: SignalConfig) -> Dict[str, str]:
        logger.info("Fetching OHLC data for %s on %s", config.symbol, config.exchange.__class__.__name__)
        candles = config.exchange.fetch_ohlc(config.symbol, config.interval)
        close_prices = [candle.close for candle in candles]

        signals = self.generate_signals(config, candles, close_prices)
        message = self.formatter(config.symbol, signals)
        logger.info("Sending Telegram notification: %s", message)
        config.telegram_notifier.send_message(message)
        return signals

    def generate_signals(self, config: SignalConfig, candles: List[OHLCV], close_prices: List[float]) -> Dict[str, str]:
        results: Dict[str, str] = {}

        try:
            fast_ema = indicators.ema(close_prices, config.ema_fast)
            slow_ema = indicators.ema(close_prices, config.ema_slow)
        except ValueError as error:
            logger.warning("Не удалось рассчитать EMA: %s", error)
        else:
            if patterns.ema_crossover(fast_ema, slow_ema):
                results["ema_crossover"] = "EMA-%d пересек EMA-%d вверх" % (config.ema_fast, config.ema_slow)

        try:
            rsi_values = indicators.rsi(close_prices, config.rsi_period)
        except ValueError as error:
            logger.warning("Не удалось рассчитать RSI: %s", error)
        else:
            if patterns.rsi_oversold(rsi_values):
                results["rsi_oversold"] = "RSI ниже %d — рынок перепродан" % config.rsi_period

        try:
            macd_line, signal_line, histogram = indicators.macd(close_prices)
        except ValueError as error:
            logger.warning("Не удалось рассчитать MACD: %s", error)
        else:
            results["macd"] = "MACD %.2f, сигнал %.2f, гистограмма %.2f" % (
                macd_line[-1], signal_line[-1], histogram[-1]
            )

        try:
            _upper_band, _mid_band, lower_band = indicators.bollinger_bands(
                close_prices, config.bollinger_period, config.bollinger_std_dev
            )
        except ValueError as error:
            logger.warning("Не удалось рассчитать полосы Боллинджера: %s", error)
        else:
            if patterns.bollinger_bounce(close_prices, lower_band):
                results["bollinger_bounce"] = "Цена отскочила от нижней полосы Боллинджера"

        results.setdefault("summary", "Нет сильных сигналов — наблюдаем")
        return results

    @staticmethod
    def default_formatter(symbol: str, signals: Dict[str, str]) -> str:
        parts = [f"{symbol} сигналы:"]
        for key, value in signals.items():
            parts.append(f"- {key}: {value}")
        return "\n".join(parts)
