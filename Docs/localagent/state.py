"""State machine: task queue, session history, activity tracking."""
import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import config

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State machine states
# ---------------------------------------------------------------------------
class AgentState(Enum):
    IDLE = "idle"
    RECEIVING = "receiving"
    PLANNING = "planning"
    EXECUTING = "executing"
    RESPONDING = "responding"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class Message:
    role: str           # user | assistant | tool | system
    content: str
    tool_name: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_ollama(self) -> dict:
        """Convert to Ollama /api/chat message format."""
        d: dict = {"role": self.role, "content": self.content}
        if self.tool_name:
            d["name"] = self.tool_name
        return d


@dataclass
class Task:
    session_id: str         # maps to Telegram chat_id
    message: str            # raw user text
    reply_to: int           # Telegram chat_id for response
    task_id: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    )
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# State manager
# ---------------------------------------------------------------------------
class StateManager:
    def __init__(self) -> None:
        self.current_state: AgentState = AgentState.IDLE
        self.queue: asyncio.Queue[Task] = asyncio.Queue()
        self._last_activity: dict[str, datetime] = {}
        config.ensure_dirs()

    # ── state machine ──────────────────────────────────────────────────────
    def transition(self, new_state: AgentState) -> None:
        log.debug("State: %s → %s", self.current_state.value, new_state.value)
        self.current_state = new_state

    # ── queue ──────────────────────────────────────────────────────────────
    async def enqueue(self, task: Task) -> None:
        await self.queue.put(task)

    async def dequeue(self) -> Task:
        return await self.queue.get()

    # ── session history (JSON + Markdown mirror) ───────────────────────────
    def load_session(self, session_id: str) -> list[dict]:
        path = config.SESSIONS_DIR / f"{session_id}.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                log.warning("Corrupt session %s — starting fresh.", session_id)
        return []

    def save_session(self, session_id: str, messages: list[dict]) -> None:
        # Trim to MAX_CONTEXT_MESSAGES (keep system prompt if present)
        if len(messages) > config.MAX_CONTEXT_MESSAGES:
            system = [m for m in messages if m.get("role") == "system"]
            rest = [m for m in messages if m.get("role") != "system"]
            rest = rest[-(config.MAX_CONTEXT_MESSAGES - len(system)):]
            messages = system + rest

        json_path = config.SESSIONS_DIR / f"{session_id}.json"
        json_path.write_text(json.dumps(messages, indent=2, ensure_ascii=False))

        # Markdown mirror for human readability
        md_path = config.SESSIONS_DIR / f"{session_id}.md"
        lines = [f"# Session {session_id}\n\n"]
        for msg in messages:
            role = msg.get("role", "?").upper()
            content = msg.get("content") or ""
            ts = msg.get("timestamp", "")
            lines.append(f"## [{role}] {ts}\n\n{content}\n\n---\n\n")
        md_path.write_text("".join(lines), encoding="utf-8")

    # ── activity tracking (for idle nudge) ────────────────────────────────
    def record_activity(self, session_id: str) -> None:
        self._last_activity[session_id] = datetime.now(timezone.utc)

    def get_last_activity(self, session_id: str) -> Optional[datetime]:
        return self._last_activity.get(session_id)

    def get_all_sessions(self) -> list[str]:
        return [p.stem for p in config.SESSIONS_DIR.glob("*.json")]
