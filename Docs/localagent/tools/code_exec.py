"""Restricted Python code executor — subprocess with timeout and output cap."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import config


def code_exec(code: str, timeout: int = 15) -> str:
    """Write *code* to a temp file and execute it with a timeout.

    Security:
    - Runs in workspace tmp dir (not system /tmp)
    - timeout enforced by subprocess
    - No shell=True
    - Output capped at MAX_SHELL_OUTPUT_BYTES
    """
    timeout = min(timeout, config.CODE_EXEC_TIMEOUT_SEC)
    config.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        dir=str(config.TEMP_DIR),
        suffix=".py",
        mode="w",
        encoding="utf-8",
        delete=False,
    ) as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)

    try:
        proc = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(config.WORKSPACE_ROOT),
            shell=False,
            env={
                # Minimal safe env — no HOME, no PATH tricks
                "PYTHONPATH": "",
                "HOME": str(config.WORKSPACE_ROOT),
            },
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
        return f"[ERROR] Code timed out after {timeout}s."
    except Exception as exc:
        return f"[ERROR] {type(exc).__name__}: {exc}"
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
