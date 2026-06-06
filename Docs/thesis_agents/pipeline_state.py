"""JSON-backed shared pipeline state with atomic persistence."""
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config

log = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _word_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").split())


def _citation_count(path: Path) -> int:
    """Count \\[N\\] style citations in markdown."""
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    return len(set(re.findall(r"\\\[(\d+)\\\]", text)))


class PipelineState:
    """Manages persistent state across pipeline cycles."""

    def __init__(self) -> None:
        config.ensure_dirs()
        self._path = config.PIPELINE_STATE_FILE
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                log.warning("Corrupt state — reinitializing.")
        return self._default()

    def _default(self) -> dict[str, Any]:
        return {
            "cycle_count": 0,
            "last_cycle_timestamp": "",
            "current_paper_version": 4,
            "current_paper_path": str(config.CURRENT_PAPER),
            "paper_hash": _hash_file(config.CURRENT_PAPER),
            "paper_word_count": _word_count(config.CURRENT_PAPER),
            "paper_citation_count": _citation_count(config.CURRENT_PAPER),
            "literature_entry_count": 0,
            "review_history": [],
            "improvement_log": [],
            "cycle_timestamps": [],
        }

    def save(self) -> None:
        self._path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ── read-only ──────────────────────────────────────────────────────────
    @property
    def cycle_count(self) -> int:
        return self._data["cycle_count"]

    @property
    def current_paper_version(self) -> int:
        return self._data["current_paper_version"]

    @property
    def current_paper_path(self) -> Path:
        return Path(self._data["current_paper_path"])

    @property
    def paper_hash(self) -> str:
        return self._data["paper_hash"]

    @property
    def review_history(self) -> list[dict]:
        return self._data["review_history"]

    @property
    def improvement_log(self) -> list[dict]:
        return self._data["improvement_log"]

    # ── mutations ──────────────────────────────────────────────────────────
    def begin_cycle(self) -> int:
        self._data["cycle_count"] += 1
        self._data["last_cycle_timestamp"] = _now_iso()
        self._data["cycle_timestamps"].append(_now_iso())
        self.save()
        return self._data["cycle_count"]

    def advance_paper_version(self, new_path: Path) -> None:
        self._data["current_paper_version"] += 1
        self._data["current_paper_path"] = str(new_path)
        self._data["paper_hash"] = _hash_file(new_path)
        self._data["paper_word_count"] = _word_count(new_path)
        self._data["paper_citation_count"] = _citation_count(new_path)
        self.save()

    def record_literature_count(self, count: int) -> None:
        self._data["literature_entry_count"] = count
        self.save()

    def record_review(self, cycle: int, summary: dict) -> None:
        self._data["review_history"].append({
            "cycle": cycle, "timestamp": _now_iso(), **summary,
        })
        self.save()

    def record_improvement(self, cycle: int, summary: dict) -> None:
        self._data["improvement_log"].append({
            "cycle": cycle, "timestamp": _now_iso(), **summary,
        })
        self.save()

    def snapshot_paper(self, cycle: int) -> Path:
        src = self.current_paper_path
        if not src.exists():
            raise FileNotFoundError(f"Paper not found: {src}")
        dest = config.VERSIONS_DIR / f"V{self.current_paper_version}_cycle{cycle}.md"
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        log.info("Snapshot: %s -> %s", src.name, dest.name)
        return dest


# ---------------------------------------------------------------------------
# Knowledge graph I/O
# ---------------------------------------------------------------------------
def load_knowledge_graph() -> list[dict]:
    if config.KNOWLEDGE_GRAPH_FILE.exists():
        try:
            return json.loads(
                config.KNOWLEDGE_GRAPH_FILE.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError:
            log.warning("Corrupt knowledge graph — empty list.")
    return []


def save_knowledge_graph(entries: list[dict]) -> None:
    config.ensure_dirs()
    config.KNOWLEDGE_GRAPH_FILE.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
