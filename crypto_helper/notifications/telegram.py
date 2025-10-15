"""Telegram notifier implementation."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from .._compat import requests

logger = logging.getLogger(__name__)


@dataclass
class TelegramNotifier:
    token: str
    chat_id: str
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        self.session = self.session or requests.Session()

    def send_message(self, text: str) -> bool:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        response = self.session.post(url, json=payload, timeout=10)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network errors are logged
            logger.error("Failed to send Telegram message: %s", exc)
            return False
        return True
