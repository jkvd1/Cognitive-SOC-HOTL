"""MCP-compliant tool definitions (JSON Schema 2020-12)."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Tool registry — each entry is a valid Ollama /api/chat tools[] element.
# Format mirrors OpenAI function-calling schema, which Ollama accepts.
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict] = [
    # ── Filesystem ──────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "fs_read",
            "description": (
                "Read the text content of a file inside the workspace. "
                "Use path relative to workspace root (e.g., 'output/report.md')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the workspace.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fs_write",
            "description": (
                "Write or overwrite a file inside the workspace. "
                "Parent directories are created automatically."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path within workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to write.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    # ── Shell ───────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "shell_exec",
            "description": (
                "Execute a shell command inside the workspace sandbox. "
                "cwd is automatically set to the workspace root. "
                "Dangerous commands are blocked."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command string to execute.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max execution time in seconds (default 30).",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        },
    },
    # ── Web ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "web_request",
            "description": (
                "Make an HTTP GET or POST request to an allowlisted URL. "
                "Only domains in ALLOWED_DOMAINS env var are permitted."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL to request."},
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST"],
                        "default": "GET",
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional request body for POST.",
                    },
                    "headers": {
                        "type": "object",
                        "description": "Optional HTTP headers as key-value pairs.",
                    },
                },
                "required": ["url"],
            },
        },
    },
    # ── Task manager ────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "task_manager",
            "description": (
                "Manage a structured personal task list with priorities and deadlines. "
                "Operations: list, add, update, delete, done."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["list", "add", "update", "delete", "done"],
                        "description": "CRUD operation to perform.",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID (required for update, delete, done).",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required for add).",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description.",
                    },
                    "priority": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "description": "Priority 1 (low) to 5 (critical).",
                    },
                    "deadline": {
                        "type": "string",
                        "description": "Deadline in ISO 8601 format (e.g. 2025-04-20T23:59:00).",
                    },
                    "filter_status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "done", "all"],
                        "description": "Filter tasks by status (for list operation).",
                        "default": "all",
                    },
                },
                "required": ["operation"],
            },
        },
    },
    # ── Calendar ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "calendar_tool",
            "description": (
                "Read or write calendar events as ICS files in the workspace/calendar directory."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["list", "add", "delete"],
                        "description": "Calendar operation.",
                    },
                    "title": {"type": "string", "description": "Event title."},
                    "start": {
                        "type": "string",
                        "description": "Event start datetime (ISO 8601).",
                    },
                    "end": {
                        "type": "string",
                        "description": "Event end datetime (ISO 8601).",
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description.",
                    },
                    "event_id": {
                        "type": "string",
                        "description": "Event UID (for delete).",
                    },
                    "days_ahead": {
                        "type": "integer",
                        "description": "List events within N days from now.",
                        "default": 7,
                    },
                },
                "required": ["operation"],
            },
        },
    },
    # ── Note search ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "note_search",
            "description": (
                "Full-text search across all Markdown files in the workspace. "
                "Returns matching lines with file path and line number."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword or phrase.",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether search is case-sensitive.",
                        "default": False,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        },
    },
    # ── Code executor ───────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "code_exec",
            "description": (
                "Execute a Python code snippet in a restricted subprocess. "
                "Returns stdout and stderr. No network access inside executed code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max runtime in seconds (default 15).",
                        "default": 15,
                    },
                },
                "required": ["code"],
            },
        },
    },
    # ── RSS fetcher ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "rss_fetch",
            "description": (
                "Fetch and parse RSS/Atom feed entries. "
                "If no URL is provided, fetches from configured RSS_FEEDS env var."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Optional specific RSS feed URL.",
                    },
                    "keyword_filter": {
                        "type": "string",
                        "description": "Only return entries matching this keyword.",
                    },
                    "max_entries": {
                        "type": "integer",
                        "description": "Maximum number of entries to return per feed.",
                        "default": 10,
                    },
                },
                "required": [],
            },
        },
    },
]


def get_all() -> list[dict]:
    """Return all MCP tool definitions."""
    return TOOL_DEFINITIONS


def get_names() -> set[str]:
    return {t["function"]["name"] for t in TOOL_DEFINITIONS}
