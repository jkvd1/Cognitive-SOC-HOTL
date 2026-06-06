"""Full-text search across Markdown files in the workspace."""
from __future__ import annotations

import config


def note_search(
    query: str,
    case_sensitive: bool = False,
    max_results: int = 20,
) -> str:
    """Search all .md files in workspace for *query*."""
    if not query.strip():
        return "[ERROR] Query cannot be empty."

    compare_query = query if case_sensitive else query.lower()
    results: list[str] = []

    for md_file in config.WORKSPACE_ROOT.rglob("*.md"):
        # Skip session files to avoid recursive noise
        if "sessions" in md_file.parts:
            continue
        try:
            lines = md_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        rel = md_file.relative_to(config.WORKSPACE_ROOT)
        for i, line in enumerate(lines, start=1):
            compare_line = line if case_sensitive else line.lower()
            if compare_query in compare_line:
                results.append(f"{rel}:{i}: {line.strip()}")
                if len(results) >= max_results:
                    break
        if len(results) >= max_results:
            break

    if not results:
        return f"No matches found for {query!r}."
    header = f"🔍 Found {len(results)} match(es) for {query!r}:\n\n"
    return header + "\n".join(results)
