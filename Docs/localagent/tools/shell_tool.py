"""Sandboxed shell command execution."""
from __future__ import annotations

import shlex
import subprocess

import config


def shell_exec(command: str, timeout: int = 30) -> str:
    """Execute *command* inside workspace root.

    Security constraints:
    - shell=False (argument list, not shell string)
    - cwd=WORKSPACE_ROOT
    - Blocklist checked before execution
    - stdout+stderr capped at MAX_SHELL_OUTPUT_BYTES
    """
    # --- Blocklist check (prefix match) ---
    cmd_lower = command.strip().lower()
    for blocked in config.SHELL_BLOCKLIST:
        if cmd_lower.startswith(blocked.lower()) or blocked.lower() in cmd_lower:
            raise PermissionError(f"Blocked command pattern: {blocked!r}")

    timeout = min(timeout, config.SHELL_TIMEOUT_SEC)

    try:
        args = shlex.split(command)
    except ValueError as exc:
        return f"[ERROR] Command parse failed: {exc}"

    try:
        proc = subprocess.run(
            args,
            cwd=str(config.WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        stdout = proc.stdout[: config.MAX_SHELL_OUTPUT_BYTES]
        stderr = proc.stderr[: config.MAX_SHELL_OUTPUT_BYTES]
        parts = [f"[EXIT {proc.returncode}]"]
        if stdout:
            parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            parts.append(f"STDERR:\n{stderr}")
        return "\n".join(parts) or "[OK] No output."
    except subprocess.TimeoutExpired:
        return f"[ERROR] Command timed out after {timeout}s."
    except FileNotFoundError:
        return f"[ERROR] Command not found: {args[0]!r}"
    except Exception as exc:
        return f"[ERROR] {type(exc).__name__}: {exc}"
