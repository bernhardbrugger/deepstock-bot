"""Telegram alert delivery."""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}"


def send_message(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    disable_preview: bool = True,
) -> bool:
    """Send a message via Telegram Bot API.

    Args:
        token: Telegram bot token.
        chat_id: Target chat ID.
        text: Message text (HTML or Markdown).
        parse_mode: Parse mode (HTML or Markdown).
        disable_preview: Disable link previews.

    Returns:
        True if message was sent successfully.
    """
    url = f"{TELEGRAM_API.format(token=token)}/sendMessage"
    chunks = _split_message(text, max_length=4000)

    for chunk in chunks:
        try:
            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": parse_mode,
                "disable_web_page_preview": disable_preview,
            }, timeout=30)
            response.raise_for_status()
            result = response.json()
            if not result.get("ok"):
                logger.error("Telegram API error: %s", result.get("description", "unknown"))
                return False
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Telegram message: %s", e)
            return False

    logger.info("Sent Telegram alert to chat %s", chat_id)
    return True


def _split_message(text: str, max_length: int = 4000) -> list[str]:
    """Split a long message into chunks respecting Telegram limits."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    return chunks
