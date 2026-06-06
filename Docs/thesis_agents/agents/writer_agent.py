"""Agent 3 — Paper Writer / Improver.

Applies targeted section improvements based on Agent 2's review findings.
Uses structural text operations — no external AI API needed.
"""
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config
from pipeline_state import load_knowledge_graph

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Improvement strategies (mapped to review categories)
# ---------------------------------------------------------------------------
def _fix_missing_citations(
    text: str, finding: dict, kg: list[dict],
) -> tuple[str, str]:
    """Insert citations from KG where unsupported claims are found."""
    description = finding.get("description", "")

    # Find the claim context in the text
    claim_match = re.search(r"'\.\.\.(.{20,60})\.\.\.'", description)
    if not claim_match:
        return text, ""

    claim_fragment = claim_match.group(1).strip()

    # Find relevant KG entries for this section area
    section = finding.get("section", "").lower()
    relevant_kg = [
        e for e in kg
        if e.get("relevance_score", 0) > 0.2
        and e.get("doi")
    ]

    if not relevant_kg:
        return text, ""

    # Pick best matching KG entry
    best = max(relevant_kg, key=lambda e: e.get("relevance_score", 0))

    # Try to find the claim in text and add citation after it
    escaped = re.escape(claim_fragment[:30])
    match = re.search(escaped, text, re.IGNORECASE)
    if match:
        # Find end of sentence
        end_pos = text.find(".", match.end())
        if end_pos != -1 and end_pos - match.end() < 200:
            # Insert citation before the period
            citation_note = f" [{best.get('id', 'NEW')}]"
            new_text = text[:end_pos] + citation_note + text[end_pos:]
            change = f"Added citation {best.get('id')} near '{claim_fragment[:40]}...'"
            return new_text, change

    return text, ""


def _fix_uncited_literature(
    text: str, finding: dict, kg: list[dict],
) -> tuple[str, str]:
    """Add reference to uncited but relevant literature."""
    lit_id = finding.get("supporting_literature", "")
    if not lit_id:
        return text, ""

    entry = next((e for e in kg if e.get("id") == lit_id), None)
    if not entry:
        return text, ""

    title = entry.get("title", "Unknown")
    authors = entry.get("authors", "")
    year = entry.get("year", "")
    doi = entry.get("doi", "")

    # Find the Landasan Teori / Related Work section
    ref_insert = f"\n\nStudi terbaru oleh {authors} ({year}) tentang \"{title}\" memberikan kontribusi relevan terhadap penelitian ini"
    if doi:
        ref_insert += f" (DOI: {doi})"
    ref_insert += ".\n"

    # Insert before the first ## after Landasan Teori
    lt_match = re.search(r"(##\s+[A-Z]\..*?Landasan\s+Teori)", text)
    if not lt_match:
        lt_match = re.search(r"(#\s+II\.)", text)

    if lt_match:
        # Find the end of the Landasan Teori section (next # heading)
        section_start = lt_match.end()
        next_section = re.search(r"\n#\s+[IVX]+\.", text[section_start:])
        if next_section:
            insert_pos = section_start + next_section.start()
            new_text = text[:insert_pos] + ref_insert + text[insert_pos:]
            change = f"Added reference to '{title[:50]}...' in Landasan Teori"
            return new_text, change

    return text, ""


def _fix_abstract_length(text: str, finding: dict) -> tuple[str, str]:
    """Flag abstract issues — structural fix only (no AI rewrite)."""
    # We can't rewrite content without AI, but we can add a TODO comment
    abstract_match = re.search(r"(_Abstrak_-)(.*?)(\n\n)", text, re.DOTALL)
    if abstract_match:
        abstract_text = abstract_match.group(2)
        word_count = len(abstract_text.split())
        if word_count < 100:
            todo = "\n\n<!-- TODO: Expand abstract to 150-250 words. Cover: problem, approach, results, significance. -->\n"
            insert_pos = abstract_match.end()
            new_text = text[:insert_pos] + todo + text[insert_pos:]
            return new_text, f"Added TODO marker for abstract expansion ({word_count} words)"
    return text, ""


def _fix_methodology_gap(text: str, finding: dict) -> tuple[str, str]:
    """Add methodology TODO markers for missing elements."""
    description = finding.get("description", "")
    suggested_fix = finding.get("suggested_fix", "")

    # Find methodology section
    method_match = re.search(r"(#+\s+.*?[Mm]etodologi.*?\n)", text)
    if not method_match:
        method_match = re.search(r"(#\s+IV\.)", text)

    if method_match:
        todo = f"\n\n<!-- REVIEW-TODO: {description}\nSuggested: {suggested_fix} -->\n"
        insert_pos = method_match.end()
        new_text = text[:insert_pos] + todo + text[insert_pos:]
        change = f"Added methodology TODO: {description[:60]}..."
        return new_text, change

    return text, ""


def _fix_equation_numbering(text: str) -> tuple[str, str]:
    """Fix equation numbering gaps."""
    tags = re.findall(r"\\tag\{(\d+)\}", text)
    if not tags:
        return text, ""

    nums = [int(t) for t in tags]
    expected = list(range(1, len(nums) + 1))

    if nums == expected:
        return text, ""

    # Build renumbering map
    new_text = text
    changes = []
    for old_num, new_num in zip(nums, expected):
        if old_num != new_num:
            new_text = new_text.replace(f"\\tag{{{old_num}}}", f"\\tag{{{new_num}}}")
            changes.append(f"{old_num}->{new_num}")

    if changes:
        return new_text, f"Renumbered equations: {', '.join(changes[:5])}"
    return text, ""


# ---------------------------------------------------------------------------
# Fix dispatcher
# ---------------------------------------------------------------------------
_FIX_MAP: dict[str, Any] = {
    "unsupported_claim": _fix_missing_citations,
    "literature_coverage": _fix_uncited_literature,
    "abstract": _fix_abstract_length,
    "methodology": _fix_methodology_gap,
}


def _apply_fix(
    text: str,
    finding: dict,
    kg: list[dict],
) -> tuple[str, str]:
    """Dispatch to appropriate fix strategy."""
    category = finding.get("category", "")
    fix_fn = _FIX_MAP.get(category)

    if fix_fn is None:
        return text, ""

    # Check signature — some take KG, some don't
    import inspect
    sig = inspect.signature(fix_fn)
    param_count = len(sig.parameters)

    if param_count == 3:
        return fix_fn(text, finding, kg)
    elif param_count == 2:
        return fix_fn(text, finding)
    return text, ""


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------
def run(cycle: int) -> dict[str, Any]:
    """Apply targeted improvements based on review findings.

    Returns summary dict for state recording.
    """
    log.info("=== Agent 3: Paper Writer -- Cycle %d ===", cycle)

    # Load review findings
    findings_path = config.STATE_DIR / f"review_findings_cycle{cycle}.json"
    if not findings_path.exists():
        log.warning("No review findings for cycle %d", cycle)
        return {"error": "No review findings", "changes": []}

    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    log.info("Review findings to address: %d", len(findings))

    # Load paper
    paper_path = config.CURRENT_PAPER
    if not paper_path.exists():
        log.error("Paper not found: %s", paper_path)
        return {"error": "Paper not found"}

    text = paper_path.read_text(encoding="utf-8")
    original_hash = hash(text)

    # Load knowledge graph
    kg = load_knowledge_graph()

    # Fix equation numbering first (global operation)
    text, eq_change = _fix_equation_numbering(text)
    changes: list[str] = []
    if eq_change:
        changes.append(eq_change)

    # Apply fixes by priority: critical → major → minor
    severity_order = {"critical": 0, "major": 1, "minor": 2}
    findings.sort(key=lambda f: severity_order.get(f.get("severity", "minor"), 3))

    applied = 0
    for finding in findings:
        if applied >= config.MAX_SECTION_REWRITES_PER_CYCLE:
            log.info("Hit max rewrites per cycle (%d)", config.MAX_SECTION_REWRITES_PER_CYCLE)
            break

        text, change = _apply_fix(text, finding, kg)
        if change:
            changes.append(change)
            applied += 1
            log.info("Applied: %s", change)

    # Write new version if changes were made
    new_version_path = paper_path  # Overwrite in-place (tracker snapshots first)
    if hash(text) != original_hash:
        new_version = config.CURRENT_PAPER.stem.rstrip("0123456789")
        next_num = int(re.search(r"(\d+)", config.CURRENT_PAPER.stem).group(1)) + 1 if re.search(r"(\d+)", config.CURRENT_PAPER.stem) else 5
        new_version_path = config.WORKSPACE_ROOT / f"ProposalSkripsiV{next_num}.md"
        new_version_path.write_text(text, encoding="utf-8")
        log.info("New version: %s", new_version_path.name)
    else:
        log.info("No changes applied -- paper unchanged")

    # Write improvement log
    improvements_path = config.STATE_DIR / f"improvements_cycle{cycle}.md"
    _write_improvement_log(changes, cycle, improvements_path)

    summary = {
        "findings_processed": len(findings),
        "changes_applied": len(changes),
        "changes": changes[:10],
        "new_paper_path": str(new_version_path) if hash(text) != original_hash else "",
    }
    log.info("Agent 3 complete: %d changes applied", len(changes))
    return summary


def _write_improvement_log(
    changes: list[str], cycle: int, path: Path,
) -> None:
    """Write improvement log for this cycle."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Paper Improvements -- Cycle {cycle}\n",
        f"_Applied: {now}_\n\n",
        f"**Changes Applied: {len(changes)}**\n\n",
    ]
    for i, change in enumerate(changes, 1):
        lines.append(f"{i}. {change}\n")

    if not changes:
        lines.append("_No changes applied this cycle._\n")

    path.write_text("".join(lines), encoding="utf-8")
