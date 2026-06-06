"""Tool dispatcher — routes MCP tool calls to handler functions."""
from __future__ import annotations

import logging
from typing import Any, Callable

from tools import fs_tool, shell_tool, web_tool, task_manager, calendar_tool, note_search, code_exec, rss_fetch

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------
class ToolResult:
    __slots__ = ("tool_name", "content", "is_error")

    def __init__(self, tool_name: str, content: str, is_error: bool = False) -> None:
        self.tool_name = tool_name
        self.content = content
        self.is_error = is_error

    def to_message(self) -> dict:
        """Convert to Ollama tool-result message format."""
        return {
            "role": "tool",
            "name": self.tool_name,
            "content": self.content,
        }


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------
_REGISTRY: dict[str, Callable[..., str]] = {
    "fs_read":       fs_tool.fs_read,
    "fs_write":      fs_tool.fs_write,
    "shell_exec":    shell_tool.shell_exec,
    "web_request":   web_tool.web_request,
    "task_manager":  task_manager.task_manager,
    "calendar_tool": calendar_tool.calendar_tool,
    "note_search":   note_search.note_search,
    "code_exec":     code_exec.code_exec,
    "rss_fetch":     rss_fetch.rss_fetch,
}


def dispatch(name: str, arguments: dict[str, Any]) -> ToolResult:
    """Execute a named tool with the given arguments.

    Returns ToolResult; never raises — errors are captured as is_error=True.
    """
    handler = _REGISTRY.get(name)
    if handler is None:
        return ToolResult(
            tool_name=name,
            content=f"[ERROR] Unknown tool: {name!r}",
            is_error=True,
        )
    try:
        result = handler(**arguments)
        return ToolResult(tool_name=name, content=str(result))
    except PermissionError as exc:
        log.error("[SECURITY] Tool %r blocked: %s", name, exc)
        return ToolResult(
            tool_name=name,
            content=f"[SECURITY ERROR] {exc}",
            is_error=True,
        )
    except Exception as exc:
        log.exception("Tool %r raised: %s", name, exc)
        return ToolResult(
            tool_name=name,
            content=f"[ERROR] {type(exc).__name__}: {exc}",
            is_error=True,
        )
