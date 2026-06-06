"""Central configuration — loads from environment, validates paths."""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "host.docker.internal")
OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_BASE_URL: str = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
ALLOWED_CHAT_IDS: set[int] = {
    int(x) for x in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if x.strip()
}

# ---------------------------------------------------------------------------
# Workspace (all agent I/O is isolated here)
# ---------------------------------------------------------------------------
WORKSPACE_ROOT: Path = Path(os.getenv("WORKSPACE_ROOT", "/workspace")).resolve()
SESSIONS_DIR: Path = WORKSPACE_ROOT / "sessions"
TASKS_DIR: Path = WORKSPACE_ROOT / "tasks"
OUTPUT_DIR: Path = WORKSPACE_ROOT / "output"
CALENDAR_DIR: Path = WORKSPACE_ROOT / "calendar"
TEMP_DIR: Path = WORKSPACE_ROOT / "tmp"

# ---------------------------------------------------------------------------
# Scheduler / heartbeat
# ---------------------------------------------------------------------------
HEARTBEAT_INTERVAL_SEC: int = int(os.getenv("HEARTBEAT_INTERVAL_SEC", "1800"))
IDLE_NUDGE_HOURS: int = int(os.getenv("IDLE_NUDGE_HOURS", "2"))
TASK_REMINDER_HORIZON_HOURS: int = int(os.getenv("TASK_REMINDER_HORIZON_HOURS", "24"))

# ---------------------------------------------------------------------------
# Network allowlist (application-level; reinforce with host iptables)
# ---------------------------------------------------------------------------
ALLOWED_DOMAINS: set[str] = {
    d.strip()
    for d in os.getenv("ALLOWED_DOMAINS", "api.telegram.org").split(",")
    if d.strip()
}

# ---------------------------------------------------------------------------
# RSS feeds (comma-separated URLs)
# ---------------------------------------------------------------------------
RSS_FEEDS: list[str] = [
    f.strip() for f in os.getenv("RSS_FEEDS", "").split(",") if f.strip()
]

# ---------------------------------------------------------------------------
# Security: shell command blocklist (prefix-matched)
# ---------------------------------------------------------------------------
SHELL_BLOCKLIST: frozenset[str] = frozenset({
    "rm -rf", "rm -r /", "dd if=", "mkfs", ":(){:|:&};:",
    "del /s", "rd /s", "shutdown", "reboot", "format c:",
    "> /dev/sda", "wget ", "curl ", "nc ", "ncat ", "python -c",
})

# ---------------------------------------------------------------------------
# Agent loop limits
# ---------------------------------------------------------------------------
MAX_TOOL_ROUNDS: int = int(os.getenv("MAX_TOOL_ROUNDS", "3"))
MAX_CONTEXT_MESSAGES: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
MAX_FILE_READ_BYTES: int = 100 * 1024          # 100 KB
MAX_SHELL_OUTPUT_BYTES: int = 10 * 1024        # 10 KB
MAX_WEB_RESPONSE_BYTES: int = 50 * 1024        # 50 KB
SHELL_TIMEOUT_SEC: int = int(os.getenv("SHELL_TIMEOUT_SEC", "30"))
CODE_EXEC_TIMEOUT_SEC: int = int(os.getenv("CODE_EXEC_TIMEOUT_SEC", "15"))


def jail_path(user_path: str) -> Path:
    """Resolve *user_path* and assert it resides within WORKSPACE_ROOT.

    Raises PermissionError on directory-traversal attempts (including
    symlink escapes).
    """
    candidate = (WORKSPACE_ROOT / user_path).resolve()
    try:
        candidate.relative_to(WORKSPACE_ROOT)
    except ValueError:
        raise PermissionError(
            f"[SECURITY] Path escape blocked: {user_path!r} → {candidate}"
        )
    return candidate


def ensure_dirs() -> None:
    """Create all required workspace sub-directories."""
    for d in (SESSIONS_DIR, TASKS_DIR, OUTPUT_DIR, CALENDAR_DIR, TEMP_DIR):
        d.mkdir(parents=True, exist_ok=True)
