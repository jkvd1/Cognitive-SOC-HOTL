"""Agent 4 — Version Tracker.

Snapshots paper before modifications, computes diffs, generates
changelog entries, manages git operations, and produces a progress dashboard.
"""
import difflib
import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config
from pipeline_state import PipelineState

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Diff computation
# ---------------------------------------------------------------------------
def _compute_diff(old_path: Path, new_path: Path) -> str:
    """Compute unified diff between two files."""
    if not old_path.exists() or not new_path.exists():
        return ""
    old_lines = old_path.read_text(encoding="utf-8").splitlines(keepends=True)
    new_lines = new_path.read_text(encoding="utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile=old_path.name,
        tofile=new_path.name,
        lineterm="",
    )
    return "\n".join(diff)


def _diff_stats(old_path: Path, new_path: Path) -> dict[str, int]:
    """Compute insertion/deletion/delta line counts."""
    if not old_path.exists():
        return {"additions": 0, "deletions": 0, "delta": 0}
    if not new_path.exists():
        return {"additions": 0, "deletions": 0, "delta": 0}

    old_lines = old_path.read_text(encoding="utf-8").splitlines()
    new_lines = new_path.read_text(encoding="utf-8").splitlines()

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    additions = 0
    deletions = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            deletions += i2 - i1
            additions += j2 - j1
        elif tag == "delete":
            deletions += i2 - i1
        elif tag == "insert":
            additions += j2 - j1

    return {
        "additions": additions,
        "deletions": deletions,
        "delta": len(new_lines) - len(old_lines),
    }


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------
def _git_is_initialized() -> bool:
    """Check if git is initialized in the workspace."""
    git_dir = config.WORKSPACE_ROOT / ".git"
    return git_dir.is_dir()


def _git_init() -> bool:
    """Initialize git repo if not present."""
    if _git_is_initialized():
        return True
    try:
        subprocess.run(
            ["git", "init"],
            cwd=str(config.WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Set default identity if not configured
        subprocess.run(
            ["git", "config", "user.email", "thesis-agent@local"],
            cwd=str(config.WORKSPACE_ROOT),
            capture_output=True, text=True, timeout=5,
        )
        subprocess.run(
            ["git", "config", "user.name", "Thesis Pipeline Agent"],
            cwd=str(config.WORKSPACE_ROOT),
            capture_output=True, text=True, timeout=5,
        )
        log.info("Git initialized in %s", config.WORKSPACE_ROOT)
        return True
    except Exception as exc:
        log.warning("Git init failed: %s", exc)
        return False


def _git_commit(message: str) -> bool:
    """Stage all tracked thesis files and commit."""
    try:
        # Add specific files (not the whole directory)
        patterns = ["ProposalSkripsi*.md", "literature_insights.md", "thesis_agents/state/*"]
        for pattern in patterns:
            subprocess.run(
                ["git", "add", pattern],
                cwd=str(config.WORKSPACE_ROOT),
                capture_output=True, text=True, timeout=10,
            )

        # Check if there are staged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--stat"],
            cwd=str(config.WORKSPACE_ROOT),
            capture_output=True, text=True, timeout=10,
        )
        if not result.stdout.strip():
            log.info("No staged changes to commit.")
            return False

        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(config.WORKSPACE_ROOT),
            capture_output=True, text=True, timeout=15,
        )
        log.info("Git commit: %s", message)
        return True
    except Exception as exc:
        log.warning("Git commit failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Changelog
# ---------------------------------------------------------------------------
def _update_changelog(
    cycle: int,
    changes: list[str],
    diff_stats: dict[str, int],
    state: PipelineState,
) -> None:
    """Prepend a new entry to CHANGELOG.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entry_lines = [
        f"## Cycle {cycle} -- {now}\n\n",
        f"**Paper Version:** V{state.current_paper_version}\n",
        f"**Lines:** +{diff_stats['additions']} / -{diff_stats['deletions']} (d{diff_stats['delta']:+d})\n\n",
    ]

    if changes:
        entry_lines.append("### Changes\n\n")
        for change in changes[:10]:
            entry_lines.append(f"- {change}\n")
        entry_lines.append("\n")
    else:
        entry_lines.append("_No changes this cycle._\n\n")

    entry_lines.append("---\n\n")
    new_entry = "".join(entry_lines)

    # Prepend to existing changelog
    existing = ""
    if config.CHANGELOG_FILE.exists():
        existing = config.CHANGELOG_FILE.read_text(encoding="utf-8")

    header = "# Thesis Pipeline Changelog\n\n"
    if existing.startswith("# "):
        # Remove existing header
        existing = existing[existing.index("\n") + 1:]

    config.CHANGELOG_FILE.write_text(
        header + new_entry + existing,
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Progress dashboard
# ---------------------------------------------------------------------------
def _generate_dashboard(state: PipelineState) -> None:
    """Generate cumulative progress dashboard."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Count findings resolved vs outstanding
    total_findings = sum(
        r.get("total_findings", 0) for r in state.review_history
    )
    total_changes = sum(
        r.get("changes_applied", 0) for r in state.improvement_log
    )

    # Word and citation count from state
    paper = state.current_paper_path
    word_count = len(paper.read_text(encoding="utf-8").split()) if paper.exists() else 0
    citations = len(set(re.findall(
        r"\[(\d+)\]",
        paper.read_text(encoding="utf-8") if paper.exists() else "",
    )))

    lines = [
        "# Thesis Pipeline -- Progress Dashboard\n\n",
        f"_Last updated: {now}_\n\n",
        "## Overview\n\n",
        f"| Metric | Value |\n",
        f"|--------|-------|\n",
        f"| Total Cycles | {state.cycle_count} |\n",
        f"| Paper Version | V{state.current_paper_version} |\n",
        f"| Word Count | {word_count:,} |\n",
        f"| Unique Citations | {citations} |\n",
        f"| Total Findings (all cycles) | {total_findings} |\n",
        f"| Total Changes Applied | {total_changes} |\n",
        f"| KG Entries | {state._data.get('literature_entry_count', 0)} |\n",
        "\n",
    ]

    # Review history table
    if state.review_history:
        lines.append("## Review History\n\n")
        lines.append("| Cycle | Findings | Critical | Major | Minor |\n")
        lines.append("|-------|----------|----------|-------|-------|\n")
        for review in state.review_history:
            sev = review.get("severity_counts", {})
            lines.append(
                f"| {review.get('cycle', '?')} "
                f"| {review.get('total_findings', 0)} "
                f"| {sev.get('critical', 0)} "
                f"| {sev.get('major', 0)} "
                f"| {sev.get('minor', 0)} |\n"
            )
        lines.append("\n")

    # Improvement log table
    if state.improvement_log:
        lines.append("## Improvement History\n\n")
        lines.append("| Cycle | Changes Applied | Key Change |\n")
        lines.append("|-------|-----------------|------------|\n")
        for imp in state.improvement_log:
            changes = imp.get("changes", [])
            key = changes[0][:50] if changes else "none"
            lines.append(
                f"| {imp.get('cycle', '?')} "
                f"| {imp.get('changes_applied', 0)} "
                f"| {key} |\n"
            )
        lines.append("\n")

    config.PROGRESS_DASHBOARD.write_text("".join(lines), encoding="utf-8")
    log.info("Dashboard updated: %s", config.PROGRESS_DASHBOARD)


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------
def run(
    cycle: int,
    state: PipelineState,
    snapshot_path: Path,
    improvement_summary: dict[str, Any],
) -> dict[str, Any]:
    """Track changes, commit, generate dashboard.

    Args:
        cycle: Current cycle number
        state: Pipeline state
        snapshot_path: Path to the pre-modification snapshot
        improvement_summary: Output from Agent 3

    Returns:
        Summary dict for state recording.
    """
    log.info("=== Agent 4: Version Tracker -- Cycle %d ===", cycle)

    current_paper = state.current_paper_path
    new_paper_path = improvement_summary.get("new_paper_path", "")

    # Compute diff if changes were made
    diff_stats = {"additions": 0, "deletions": 0, "delta": 0}
    diff_text = ""

    if new_paper_path and Path(new_paper_path).exists():
        new_path = Path(new_paper_path)
        diff_stats = _diff_stats(snapshot_path, new_path)
        diff_text = _compute_diff(snapshot_path, new_path)

        # Save diff to file
        diff_path = config.STATE_DIR / f"diff_cycle{cycle}.patch"
        diff_path.write_text(diff_text, encoding="utf-8")
        log.info("Diff saved: %s (+%d/-%d)", diff_path.name, diff_stats["additions"], diff_stats["deletions"])

        # Update state to point to new paper
        state.advance_paper_version(new_path)
        # Update config to track the new paper for subsequent cycles
        config.CURRENT_PAPER = new_path
    else:
        log.info("No new paper version -- no diff to compute")

    # Update changelog
    changes = improvement_summary.get("changes", [])
    _update_changelog(cycle, changes, diff_stats, state)

    # Git operations
    git_committed = False
    if _git_init():
        commit_msg = f"cycle-{cycle}: {len(changes)} changes applied"
        if changes:
            commit_msg += f" | {changes[0][:50]}"
        git_committed = _git_commit(commit_msg)

    # Generate progress dashboard
    _generate_dashboard(state)

    summary = {
        "diff_stats": diff_stats,
        "git_committed": git_committed,
        "changelog_updated": True,
        "dashboard_updated": True,
        "new_paper_version": state.current_paper_version,
    }
    log.info("Agent 4 complete: %s", summary)
    return summary
