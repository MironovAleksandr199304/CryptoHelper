"""Entry point for running the CryptoHelper signal engine from the command line."""
from __future__ import annotations

import argparse
import logging
import os

from crypto_helper import (
    BinanceClient,
    BybitClient,
    KuCoinClient,
    SignalConfig,
    SignalEngine,
    TelegramNotifier,
)

logging.basicConfig(level=logging.INFO)

EXCHANGES = {
    "binance": BinanceClient,
    "bybit": BybitClient,
    "kucoin": KuCoinClient,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CryptoHelper signal engine")
    parser.add_argument("symbol", help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("interval", help="Candle interval (1m, 1h, 1d, etc.)")
    parser.add_argument(
        "--exchange",
        choices=EXCHANGES.keys(),
        default="binance",
        help="Exchange to fetch data from",
    )
    parser.add_argument("--ema-fast", type=int, default=50)
    parser.add_argument("--ema-slow", type=int, default=200)
    parser.add_argument("--rsi-period", type=int, default=14)
    parser.add_argument("--bollinger-period", type=int, default=20)
    parser.add_argument("--bollinger-std", type=float, default=2.0)
    parser.add_argument(
        "--candles-limit",
        type=int,
        default=None,
        help="Override automatically computed candle history size",
    )
    parser.add_argument("--telegram-token", default=os.getenv("TELEGRAM_TOKEN"))
    parser.add_argument("--telegram-chat", default=os.getenv("TELEGRAM_CHAT_ID"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.telegram_token or not args.telegram_chat:
        raise SystemExit("Telegram token and chat ID must be provided")

    exchange_cls = EXCHANGES[args.exchange]
    exchange = exchange_cls()
    notifier = TelegramNotifier(token=args.telegram_token, chat_id=args.telegram_chat)

    config = SignalConfig(
        symbol=args.symbol,
        interval=args.interval,
        exchange=exchange,
        telegram_notifier=notifier,
        candles_limit=args.candles_limit,
        ema_fast=args.ema_fast,
        ema_slow=args.ema_slow,
        rsi_period=args.rsi_period,
        bollinger_period=args.bollinger_period,
        bollinger_std_dev=args.bollinger_std,
    )

    engine = SignalEngine()
    signals = engine.run(config)
    for name, description in signals.items():
        logging.info("%s: %s", name, description)


if __name__ == "__main__":
    main()
