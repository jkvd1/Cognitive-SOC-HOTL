"""Entry point — infinite loop scheduler running 4-agent pipeline every 5 hours.

Usage:
    python main.py              # Infinite loop (default)
    python main.py --once       # Single cycle, then exit
    python main.py --dry-run    # Preview config, no execution
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

import config
from pipeline_state import PipelineState

# Agent imports
from agents import literature_agent
from agents import reviewer_agent
from agents import writer_agent
from agents import tracker_agent

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def _setup_logging() -> None:
    config.ensure_dirs()
    handlers = [
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace", closefd=False)
        ),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ]
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )

log = logging.getLogger("pipeline")


# ---------------------------------------------------------------------------
# Single pipeline cycle
# ---------------------------------------------------------------------------
def run_cycle(state: PipelineState) -> dict:
    """Execute one full 4-agent pipeline cycle. Returns cycle summary."""
    # Sync config.CURRENT_PAPER from persisted state (tracks V5, V6, etc.)
    if state.current_paper_path.exists():
        config.CURRENT_PAPER = state.current_paper_path

    cycle = state.begin_cycle()
    log.info("=" * 70)
    log.info("CYCLE %d STARTED -- %s", cycle, datetime.now(timezone.utc).isoformat())
    log.info("Paper: %s", config.CURRENT_PAPER)
    log.info("=" * 70)

    results: dict = {"cycle": cycle, "agents": {}}

    # ── AGENT 4 PRE-STEP: Snapshot current paper ──────────────────────────
    try:
        snapshot_path = state.snapshot_paper(cycle)
        log.info("Paper snapshot saved: %s", snapshot_path.name)
    except FileNotFoundError as exc:
        log.error("Cannot snapshot paper: %s", exc)
        snapshot_path = config.CURRENT_PAPER
    except Exception as exc:
        log.error("Snapshot failed: %s", exc)
        snapshot_path = config.CURRENT_PAPER

    # ── AGENT 1: Literature Scholar ───────────────────────────────────────
    try:
        log.info(">> Starting Agent 1: Literature Scholar")
        lit_result = literature_agent.run(cycle)
        results["agents"]["literature"] = lit_result
        state.record_literature_count(lit_result.get("total_kg_entries", 0))
        log.info("[OK] Agent 1 complete")
    except Exception as exc:
        log.error("[FAIL] Agent 1 failed: %s\n%s", exc, traceback.format_exc())
        results["agents"]["literature"] = {"error": str(exc)}

    # ── AGENT 2: Paper Reviewer ───────────────────────────────────────────
    try:
        log.info(">> Starting Agent 2: Paper Reviewer")
        review_result = reviewer_agent.run(cycle)
        results["agents"]["reviewer"] = review_result
        state.record_review(cycle, review_result)
        log.info("[OK] Agent 2 complete")
    except Exception as exc:
        log.error("[FAIL] Agent 2 failed: %s\n%s", exc, traceback.format_exc())
        results["agents"]["reviewer"] = {"error": str(exc)}

    # ── AGENT 3: Paper Writer ─────────────────────────────────────────────
    try:
        log.info(">> Starting Agent 3: Paper Writer")
        writer_result = writer_agent.run(cycle)
        results["agents"]["writer"] = writer_result
        state.record_improvement(cycle, writer_result)
        log.info("[OK] Agent 3 complete")
    except Exception as exc:
        log.error("[FAIL] Agent 3 failed: %s\n%s", exc, traceback.format_exc())
        results["agents"]["writer"] = {"error": str(exc)}
        writer_result = {"changes": [], "new_paper_path": ""}

    # ── AGENT 4: Version Tracker ──────────────────────────────────────────
    try:
        log.info(">> Starting Agent 4: Version Tracker")
        tracker_result = tracker_agent.run(
            cycle, state, snapshot_path, writer_result
        )
        results["agents"]["tracker"] = tracker_result
        log.info("[OK] Agent 4 complete")
    except Exception as exc:
        log.error("[FAIL] Agent 4 failed: %s\n%s", exc, traceback.format_exc())
        results["agents"]["tracker"] = {"error": str(exc)}

    log.info("=" * 70)
    log.info("CYCLE %d COMPLETE", cycle)
    log.info("=" * 70)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-Agent Thesis Pipeline — Antigravity-Native"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single cycle and exit.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print config and exit without running.",
    )
    args = parser.parse_args()

    _setup_logging()

    if args.dry_run:
        print("=== DRY RUN — Configuration ===")
        print(f"  Workspace:       {config.WORKSPACE_ROOT}")
        print(f"  Paper:           {config.CURRENT_PAPER}")
        print(f"  Paper exists:    {config.CURRENT_PAPER.exists()}")
        print(f"  State dir:       {config.STATE_DIR}")
        print(f"  Cycle interval:  {config.CYCLE_INTERVAL_HOURS}h ({config.CYCLE_INTERVAL_SEC}s)")
        print(f"  Search topics:   {len(config.SEARCH_TOPICS)}")
        print(f"  Max rewrites:    {config.MAX_SECTION_REWRITES_PER_CYCLE}")
        print(f"  Log file:        {config.LOG_FILE}")
        return

    state = PipelineState()

    log.info("Pipeline initialized | workspace=%s | interval=%sh",
             config.WORKSPACE_ROOT, config.CYCLE_INTERVAL_HOURS)

    if args.once:
        log.info("Mode: SINGLE CYCLE")
        run_cycle(state)
        log.info("Single cycle complete. Exiting.")
        return

    # ── Infinite loop ─────────────────────────────────────────────────────
    log.info("Mode: INFINITE LOOP (every %sh)", config.CYCLE_INTERVAL_HOURS)
    log.info("Press Ctrl+C to stop.")

    while True:
        try:
            run_cycle(state)
        except KeyboardInterrupt:
            log.info("Interrupted by user. Stopping.")
            break
        except Exception as exc:
            log.error("Cycle failed catastrophically: %s\n%s",
                      exc, traceback.format_exc())

        # Sleep until next cycle
        next_run = datetime.now(timezone.utc).timestamp() + config.CYCLE_INTERVAL_SEC
        next_run_str = datetime.fromtimestamp(
            next_run, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC")
        log.info(
            "Next cycle at %s (sleeping %ds / %.1fh)",
            next_run_str, config.CYCLE_INTERVAL_SEC, config.CYCLE_INTERVAL_HOURS,
        )

        try:
            time.sleep(config.CYCLE_INTERVAL_SEC)
        except KeyboardInterrupt:
            log.info("Interrupted during sleep. Stopping.")
            break


if __name__ == "__main__":
    main()
