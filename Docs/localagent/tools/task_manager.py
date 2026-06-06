"""Structured task manager with priority, deadline, and status tracking."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import config

_TASKS_FILE = config.TASKS_DIR / "tasks.json"
_VALID_STATUSES = {"todo", "in_progress", "done"}
_PRIORITY_EMOJI = {5: "🔴", 4: "🟠", 3: "🟡", 2: "🔵", 1: "⚪"}


def _load() -> list[dict]:
    config.TASKS_DIR.mkdir(parents=True, exist_ok=True)
    if _TASKS_FILE.exists():
        try:
            return json.loads(_TASKS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save(tasks: list[dict]) -> None:
    _TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def _format_task(t: dict) -> str:
    emoji = _PRIORITY_EMOJI.get(t.get("priority", 3), "🟡")
    deadline = t.get("deadline", "No deadline")
    status = t.get("status", "todo")
    return (
        f"{emoji} [{t['task_id'][:8]}] P{t.get('priority',3)} | {status.upper()}\n"
        f"   📌 {t.get('title', '(no title)')}\n"
        f"   📅 {deadline}\n"
        f"   📝 {t.get('description', '')}"
    )


def task_manager(
    operation: str,
    task_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    priority: int = 3,
    deadline: str | None = None,
    filter_status: str = "all",
) -> str:
    tasks = _load()

    if operation == "list":
        filtered = tasks if filter_status == "all" else [
            t for t in tasks if t.get("status") == filter_status
        ]
        if not filtered:
            return "📋 No tasks found."
        # Sort: priority desc, deadline asc
        def sort_key(t: dict):
            dl = t.get("deadline") or "9999-12-31"
            return (-t.get("priority", 3), dl)
        filtered.sort(key=sort_key)
        lines = ["📋 **Task List**\n"]
        lines += [_format_task(t) for t in filtered]
        return "\n\n".join(lines)

    if operation == "add":
        if not title:
            return "[ERROR] title is required for add operation."
        new_task: dict[str, Any] = {
            "task_id": str(uuid.uuid4()),
            "title": title,
            "description": description or "",
            "priority": max(1, min(5, priority)),
            "deadline": deadline,
            "status": "todo",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        tasks.append(new_task)
        _save(tasks)
        return f"[OK] Task added: {_format_task(new_task)}"

    if operation in {"update", "delete", "done"}:
        if not task_id:
            return f"[ERROR] task_id required for {operation}."
        # Match by prefix
        matches = [t for t in tasks if t["task_id"].startswith(task_id)]
        if not matches:
            return f"[ERROR] No task found with id prefix: {task_id!r}"
        t = matches[0]

        if operation == "delete":
            tasks = [x for x in tasks if x["task_id"] != t["task_id"]]
            _save(tasks)
            return f"[OK] Deleted task: {t['title']!r}"

        if operation == "done":
            t["status"] = "done"
            t["updated_at"] = datetime.now(timezone.utc).isoformat()
            _save(tasks)
            return f"[OK] Marked done: {t['title']!r}"

        # update
        if title:
            t["title"] = title
        if description is not None:
            t["description"] = description
        if priority:
            t["priority"] = max(1, min(5, priority))
        if deadline:
            t["deadline"] = deadline
        t["updated_at"] = datetime.now(timezone.utc).isoformat()
        _save(tasks)
        return f"[OK] Updated: {_format_task(t)}"

    return f"[ERROR] Unknown operation: {operation!r}"


def get_pending_tasks_sorted() -> list[dict]:
    """Return todo + in_progress tasks sorted by priority desc, deadline asc.
    Used by the scheduler for heartbeat reminders.
    """
    tasks = _load()
    active = [t for t in tasks if t.get("status") in ("todo", "in_progress")]

    def sort_key(t: dict):
        dl = t.get("deadline") or "9999-12-31"
        return (-t.get("priority", 3), dl)

    active.sort(key=sort_key)
    return active
