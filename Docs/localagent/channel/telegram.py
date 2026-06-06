"""Telegram long-polling channel adapter."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

import config
from state import Task

log = logging.getLogger(__name__)

_BASE = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}"
_MAX_CHUNK = 4096


class TelegramChannel:
    def __init__(self) -> None:
        self._offset: int = 0
        self._client = httpx.AsyncClient(timeout=40.0)

    async def close(self) -> None:
        await self._client.aclose()

    # ── Polling ─────────────────────────────────────────────────────────────
    async def poll(self) -> Task | None:
        """Long-poll for one new message. Returns None on timeout/error."""
        try:
            resp = await self._client.get(
                f"{_BASE}/getUpdates",
                params={"offset": self._offset, "timeout": 30, "limit": 1},
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("Telegram poll error: %s", exc)
            await asyncio.sleep(5)
            return None

        updates: list[dict] = data.get("result", [])
        for update in updates:
            self._offset = update["update_id"] + 1
            msg = update.get("message") or update.get("edited_message")
            if not msg:
                continue
            chat_id: int = msg["chat"]["id"]
            text: str = msg.get("text", "").strip()
            if not text or chat_id not in config.ALLOWED_CHAT_IDS:
                log.debug("Ignored message from chat_id=%s", chat_id)
                continue
            log.info("Received message from %s: %r", chat_id, text[:80])
            return Task(
                session_id=str(chat_id),
                message=text,
                reply_to=chat_id,
            )
        return None

    # ── Sending ─────────────────────────────────────────────────────────────
    async def send(self, chat_id: int, text: str) -> None:
        """Send text to *chat_id*, splitting at Telegram's 4096-char limit."""
        for chunk in self._split_message(text):
            await self._send_chunk(chat_id, chunk)

    async def _send_chunk(self, chat_id: int, text: str) -> None:
        try:
            resp = await self._client.post(
                f"{_BASE}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )
            if resp.status_code != 200:
                # Retry without Markdown if formatting error
                await self._client.post(
                    f"{_BASE}/sendMessage",
                    json={"chat_id": chat_id, "text": text},
                )
        except Exception as exc:
            log.error("Telegram send failed: %s", exc)

    async def send_typing(self, chat_id: int) -> None:
        """Show typing indicator while the agent is processing."""
        try:
            await self._client.post(
                f"{_BASE}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
            )
        except Exception:
            pass

    @staticmethod
    def _split_message(text: str) -> list[str]:
        """Split at paragraph boundaries, respecting 4096-char limit."""
        if len(text) <= _MAX_CHUNK:
            return [text]
        chunks: list[str] = []
        while text:
            if len(text) <= _MAX_CHUNK:
                chunks.append(text)
                break
            split_at = text.rfind("\n\n", 0, _MAX_CHUNK)
            if split_at == -1:
                split_at = text.rfind("\n", 0, _MAX_CHUNK)
            if split_at == -1:
                split_at = _MAX_CHUNK
            chunks.append(text[:split_at].strip())
            text = text[split_at:].strip()
        return chunks
