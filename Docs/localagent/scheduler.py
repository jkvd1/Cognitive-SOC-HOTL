"""Heartbeat scheduler — proactive task reminders every 30 minutes."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import config
from tools.task_manager import get_pending_tasks_sorted

if TYPE_CHECKING:
    from channel.telegram import TelegramChannel
    from state import StateManager

log = logging.getLogger(__name__)

_PRIORITY_EMOJI = {5: "🔴", 4: "🟠", 3: "🟡", 2: "🔵", 1: "⚪"}


class Scheduler:
    def __init__(self, channel: "TelegramChannel", state: "StateManager") -> None:
        self._channel = channel
        self._state = state

    async def run(self) -> None:
        """Background loop: fire every HEARTBEAT_INTERVAL_SEC."""
        log.info("Scheduler started — interval=%ds", config.HEARTBEAT_INTERVAL_SEC)
        while True:
            await asyncio.sleep(config.HEARTBEAT_INTERVAL_SEC)
            await self._tick()

    async def _tick(self) -> None:
        """One heartbeat tick: check tasks, send reminders."""
        log.debug("Heartbeat tick at %s", datetime.now(timezone.utc).isoformat())
        tasks = get_pending_tasks_sorted()
        if not tasks:
            await self._maybe_nudge_idle()
            return

        message = self._build_reminder(tasks)
        for chat_id in config.ALLOWED_CHAT_IDS:
            await self._channel.send(chat_id, message)
            log.info("Sent task reminder to chat_id=%s (%d tasks)", chat_id, len(tasks))

    def _build_reminder(self, tasks: list[dict]) -> str:
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(hours=config.TASK_REMINDER_HORIZON_HOURS)

        urgent: list[dict] = []
        upcoming: list[dict] = []
        remaining: list[dict] = []

        for t in tasks:
            dl = t.get("deadline")
            if dl:
                try:
                    from dateutil import parser as dp
                    dt = dp.parse(dl)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    if dt < now:
                        urgent.append({"task": t, "label": "⚠️ OVERDUE"})
                    elif dt <= horizon:
                        upcoming.append({"task": t, "label": f"Due {dt.strftime('%b %d %H:%M')}"})
                    else:
                        remaining.append(t)
                except Exception:
                    remaining.append(t)
            else:
                remaining.append(t)

        lines = ["🔔 *Task Reminder* — Here's what needs your attention:\n"]

        if urgent:
            lines.append("*🚨 Overdue*")
            for item in urgent:
                t = item["task"]
                emoji = _PRIORITY_EMOJI.get(t.get("priority", 3), "🟡")
                lines.append(f"{emoji} {t['title']} — {item['label']}")
            lines.append("")

        if upcoming:
            lines.append(f"*⏰ Due within {config.TASK_REMINDER_HORIZON_HOURS}h*")
            for item in upcoming:
                t = item["task"]
                emoji = _PRIORITY_EMOJI.get(t.get("priority", 3), "🟡")
                lines.append(f"{emoji} P{t.get('priority',3)} | {t['title']} — {item['label']}")
            lines.append("")

        if remaining:
            lines.append("*📋 Other Active Tasks (by priority)*")
            for t in remaining[:5]:  # Show top 5 only
                emoji = _PRIORITY_EMOJI.get(t.get("priority", 3), "🟡")
                dl = t.get("deadline", "No deadline")
                lines.append(f"{emoji} P{t.get('priority',3)} | {t['title']} — {dl}")
            if len(remaining) > 5:
                lines.append(f"  _...and {len(remaining)-5} more_")

        lines.append("\n💬 Reply to start working on any of these!")
        return "\n".join(lines)

    async def _maybe_nudge_idle(self) -> None:
        """Send nudge if all sessions have been idle for IDLE_NUDGE_HOURS."""
        now = datetime.now(timezone.utc)
        idle_threshold = timedelta(hours=config.IDLE_NUDGE_HOURS)
        for session_id in self._state.get_all_sessions():
            last = self._state.get_last_activity(session_id)
            if last is None or (now - last) < idle_threshold:
                return  # At least one session is active — skip nudge

        # All sessions idle — send nudge to all allowed chats
        nudge = (
            "👋 *Hey! Just checking in.*\n\n"
            "No tasks in your list right now. Want me to help you plan something? "
            "Just send me a message!"
        )
        for chat_id in config.ALLOWED_CHAT_IDS:
            await self._channel.send(chat_id, nudge)
