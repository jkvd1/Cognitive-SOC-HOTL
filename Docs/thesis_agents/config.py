"""Central configuration — no API keys, pure Antigravity-native."""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE_ROOT: Path = Path(
    os.getenv("WORKSPACE_ROOT", r"c:\Users\ACER\Downloads\Skripsi")
).resolve()

PROJECT_DIR: Path = Path(__file__).parent.resolve()
STATE_DIR: Path = PROJECT_DIR / "state"
VERSIONS_DIR: Path = STATE_DIR / "versions"

# Paper paths
CURRENT_PAPER: Path = WORKSPACE_ROOT / "ProposalSkripsiV4.md"

# State files
PIPELINE_STATE_FILE: Path = STATE_DIR / "pipeline_state.json"
KNOWLEDGE_GRAPH_FILE: Path = STATE_DIR / "literature_knowledge.json"
CHANGELOG_FILE: Path = STATE_DIR / "CHANGELOG.md"
PROGRESS_DASHBOARD: Path = STATE_DIR / "progress_dashboard.md"

# Existing assets
LITERATURE_INSIGHTS: Path = WORKSPACE_ROOT / "literature_insights.md"

# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------
CYCLE_INTERVAL_HOURS: float = float(os.getenv("CYCLE_INTERVAL_HOURS", "5"))
CYCLE_INTERVAL_SEC: int = int(CYCLE_INTERVAL_HOURS * 3600)

# ---------------------------------------------------------------------------
# Agent limits
# ---------------------------------------------------------------------------
MAX_SECTION_REWRITES_PER_CYCLE: int = 5
MAX_LITERATURE_ENTRIES_PER_CYCLE: int = 10
MAX_SEARCH_RESULTS: int = 20

# ---------------------------------------------------------------------------
# Search targets (IEEE topics relevant to thesis)
# ---------------------------------------------------------------------------
SEARCH_TOPICS: list[str] = [
    "Cognitive SOC architecture AI autonomous",
    "SOAR security orchestration automation response",
    "Human-On-The-Loop cybersecurity SOC",
    "Random Forest threat classification IDS",
    "concept drift detection intrusion detection",
    "adaptive feedback loop machine learning security",
    "agentic AI security operations center",
    "threat intelligence automation SIEM integration",
    "IEEE SOC automation MTTR reduction",
    "cyber threat intelligence pipeline orchestration",
]

# ---------------------------------------------------------------------------
# IEEE review rubric weights
# ---------------------------------------------------------------------------
IEEE_RUBRIC: dict[str, float] = {
    "structure_compliance": 0.15,
    "abstract_quality": 0.10,
    "introduction_depth": 0.10,
    "literature_coverage": 0.15,
    "methodology_rigor": 0.20,
    "formalization_quality": 0.10,
    "citation_density": 0.10,
    "evaluation_design": 0.10,
}

# Required IEEE sections
IEEE_REQUIRED_SECTIONS: list[str] = [
    "Abstract",
    "Pendahuluan",       # Introduction
    "Landasan Teori",    # Related Work / Theoretical Foundation
    "Arsitektur",        # Proposed Architecture
    "Metodologi",        # Methodology
    "Keterbatasan",      # Limitations / Future Work
    "Referensi",         # References
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: Path = STATE_DIR / "pipeline.log"


def ensure_dirs() -> None:
    """Create all required directories."""
    for d in (STATE_DIR, VERSIONS_DIR):
        d.mkdir(parents=True, exist_ok=True)
