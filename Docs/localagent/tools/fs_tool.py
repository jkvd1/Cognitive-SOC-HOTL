"""Sandboxed filesystem read/write — all paths jailed to WORKSPACE_ROOT."""
from __future__ import annotations

import config


def fs_read(path: str) -> str:
    """Read a file from the workspace. Raises PermissionError on escape."""
    target = config.jail_path(path)
    if not target.exists():
        return f"[ERROR] File not found: {path!r}"
    if not target.is_file():
        return f"[ERROR] Not a file: {path!r}"
    size = target.stat().st_size
    if size > config.MAX_FILE_READ_BYTES:
        return (
            f"[ERROR] File too large ({size} bytes). "
            f"Max allowed: {config.MAX_FILE_READ_BYTES} bytes."
        )
    return target.read_text(encoding="utf-8", errors="replace")


def fs_write(path: str, content: str) -> str:
    """Write content to a file inside the workspace."""
    target = config.jail_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"[OK] Written {len(content)} chars to {path!r}."
