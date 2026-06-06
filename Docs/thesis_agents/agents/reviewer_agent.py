"""Agent 2 — Paper Reviewer with Bidirectional Knowledge Graph.

Performs structural IEEE rubric analysis on the paper and maps
findings against the literature knowledge graph bidirectionally.
No AI API needed — uses regex, NLP heuristics, and rubric scoring.
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
# Section parser
# ---------------------------------------------------------------------------
def _parse_sections(text: str) -> dict[str, str]:
    """Split markdown paper into sections by heading."""
    sections: dict[str, str] = {}
    current_heading = "preamble"
    current_lines: list[str] = []

    for line in text.split("\n"):
        heading_match = re.match(r"^#{1,3}\s+(.+)", line)
        if heading_match:
            # Save previous section
            sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = heading_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    sections[current_heading] = "\n".join(current_lines).strip()
    return sections


# ---------------------------------------------------------------------------
# Rubric analysis functions
# ---------------------------------------------------------------------------
def _check_structure(sections: dict[str, str]) -> list[dict]:
    """Check paper has all IEEE-required sections."""
    findings: list[dict] = []
    section_names = " ".join(sections.keys()).lower()

    for req in config.IEEE_REQUIRED_SECTIONS:
        if req.lower() not in section_names:
            findings.append({
                "severity": "major",
                "category": "structure",
                "section": req,
                "description": f"Required IEEE section '{req}' not found or misnamed.",
                "suggested_fix": f"Add or rename section to include '{req}'.",
            })

    return findings


def _check_abstract(sections: dict[str, str]) -> list[dict]:
    """Analyze abstract quality."""
    findings: list[dict] = []
    abstract = ""
    for key, val in sections.items():
        if "abstrak" in key.lower() or "abstract" in key.lower():
            abstract = val
            break

    # Check from preamble (IEEE abstract often before first heading)
    if not abstract:
        preamble = sections.get("preamble", "")
        if "abstrak" in preamble.lower() or "abstract" in preamble.lower():
            abstract = preamble

    if not abstract:
        findings.append({
            "severity": "critical",
            "category": "abstract",
            "section": "Abstract",
            "description": "No abstract found in the paper.",
            "suggested_fix": "Add a structured abstract (150-250 words) covering: problem, approach, key results, significance.",
        })
        return findings

    word_count = len(abstract.split())
    if word_count < 100:
        findings.append({
            "severity": "major",
            "category": "abstract",
            "section": "Abstract",
            "description": f"Abstract too short ({word_count} words). IEEE standard recommends 150-250 words.",
            "suggested_fix": "Expand abstract to cover: problem statement, methodology, expected results, significance.",
        })
    elif word_count > 300:
        findings.append({
            "severity": "minor",
            "category": "abstract",
            "section": "Abstract",
            "description": f"Abstract may be too long ({word_count} words). IEEE recommends 150-250.",
            "suggested_fix": "Trim abstract to focus on essential contributions.",
        })

    # Check for key elements
    abstract_lower = abstract.lower()
    if not any(kw in abstract_lower for kw in ["propose", "mengusulkan", "present", "menyajikan"]):
        findings.append({
            "severity": "minor",
            "category": "abstract",
            "section": "Abstract",
            "description": "Abstract lacks explicit contribution statement.",
            "suggested_fix": "Add a clear 'We propose/present...' statement.",
        })

    return findings


def _check_citations(text: str, sections: dict[str, str]) -> list[dict]:
    """Analyze citation density and distribution."""
    findings: list[dict] = []

    # Count total citations — handles \[N\], [N], and \\[N\\]
    all_citations = re.findall(r"\\?\[?(\d+)\\?\]?", text)
    # More precise: match [N] or \[N\]
    all_citations = re.findall(r"(?:\\\[|\[)(\d+)(?:\\\]|\])", text)
    unique_refs = set(all_citations)

    if len(unique_refs) < 15:
        findings.append({
            "severity": "major",
            "category": "citations",
            "section": "References",
            "description": f"Only {len(unique_refs)} unique references. IEEE papers typically have 20-40+.",
            "suggested_fix": "Add more recent references (2022-2026) from IEEE, ACM, and relevant journals.",
        })

    # Check citation density per major section
    for section_name, section_text in sections.items():
        if any(kw in section_name.lower() for kw in ["pendahuluan", "introduction", "landasan", "teori", "related"]):
            section_cites = re.findall(r"(?:\\\[|\[)(\d+)(?:\\\]|\])", section_text)
            words = len(section_text.split())
            if words > 200 and len(section_cites) < 3:
                findings.append({
                    "severity": "major",
                    "category": "citations",
                    "section": section_name,
                    "description": f"Section '{section_name}' has {len(section_cites)} citations for {words} words. Too sparse.",
                    "suggested_fix": "Add supporting citations from literature knowledge graph.",
                })

    # Check for self-citation of non-existent references
    ref_section = ""
    for key, val in sections.items():
        if "referensi" in key.lower() or "references" in key.lower():
            ref_section = val
            break

    if ref_section:
        defined_refs = set(re.findall(r"(?:\\\[|\[)(\d+)(?:\\\]|\])", ref_section))
        cited_but_undefined = unique_refs - defined_refs
        if cited_but_undefined:
            findings.append({
                "severity": "critical",
                "category": "citations",
                "section": "References",
                "description": f"Citations {cited_but_undefined} used in text but not defined in References.",
                "suggested_fix": "Add missing reference entries or remove dangling citations.",
            })

    return findings


def _check_methodology(sections: dict[str, str]) -> list[dict]:
    """Analyze methodology rigor."""
    findings: list[dict] = []
    method_text = ""
    for key, val in sections.items():
        if any(kw in key.lower() for kw in ["metodologi", "methodology", "evaluasi", "evaluation"]):
            method_text += val + "\n"

    if not method_text:
        findings.append({
            "severity": "critical",
            "category": "methodology",
            "section": "Methodology",
            "description": "No methodology section found.",
            "suggested_fix": "Add detailed methodology section covering experimental design, metrics, and analysis plan.",
        })
        return findings

    method_lower = method_text.lower()

    # Check for experimental design elements
    design_elements = {
        "baseline": ["baseline", "kontrol", "control", "manual"],
        "metrics": ["accuracy", "f1", "precision", "recall", "mttr", "fpr"],
        "statistical_test": ["t-test", "wilcoxon", "statistik", "statistical", "signifikan"],
        "sample_size": ["sample", "sampel", "responden", "n =", "n="],
    }

    for element, keywords in design_elements.items():
        if not any(kw in method_lower for kw in keywords):
            findings.append({
                "severity": "major",
                "category": "methodology",
                "section": "Methodology",
                "description": f"Methodology lacks clear '{element}' specification.",
                "suggested_fix": f"Add explicit {element} definition with justification.",
            })

    # Check for equations
    equation_count = len(re.findall(r"\$\$.+?\$\$", method_text, re.DOTALL))
    equation_count += len(re.findall(r"\\tag\{", method_text))
    if equation_count < 2:
        findings.append({
            "severity": "minor",
            "category": "methodology",
            "section": "Methodology",
            "description": f"Methodology has only {equation_count} formal equations. Consider adding more formalization.",
            "suggested_fix": "Formalize key metrics and procedures with mathematical notation.",
        })

    return findings


def _check_formalization(text: str) -> list[dict]:
    """Check mathematical formalization quality."""
    findings: list[dict] = []

    # Count equations
    tagged_eqs = re.findall(r"\\tag\{(\d+)\}", text)
    if tagged_eqs:
        # Check for sequential numbering
        nums = [int(n) for n in tagged_eqs]
        expected = list(range(1, max(nums) + 1))
        missing = set(expected) - set(nums)
        if missing:
            findings.append({
                "severity": "minor",
                "category": "formalization",
                "section": "Equations",
                "description": f"Equation numbering has gaps: missing {missing}.",
                "suggested_fix": "Renumber equations sequentially.",
            })

    # Check for undefined variables
    # Look for $var$ patterns that appear without definition nearby
    inline_math = re.findall(r"\$([^$]+)\$", text)
    if len(inline_math) > 30:
        # Paper has substantial math — good sign
        pass
    elif len(inline_math) < 5:
        findings.append({
            "severity": "minor",
            "category": "formalization",
            "section": "General",
            "description": "Paper has minimal inline mathematical notation.",
            "suggested_fix": "Add formal variable definitions and inline math where appropriate.",
        })

    return findings


def _check_kg_coverage(
    sections: dict[str, str],
    knowledge_graph: list[dict],
) -> list[dict]:
    """Bidirectional knowledge graph analysis.

    Forward:  Paper claim → Does supporting literature exist in KG?
    Backward: KG entry → Is it referenced in the paper?
    """
    findings: list[dict] = []
    paper_text = " ".join(sections.values()).lower()

    # BACKWARD: KG entries with high relevance not cited in paper
    uncited_relevant: list[dict] = []
    for entry in knowledge_graph:
        relevance = entry.get("relevance_score", 0)
        if relevance < 0.25:
            continue
        title_words = set(re.findall(r"\w{5,}", (entry.get("title") or "").lower()))
        # Check if paper references this work (by title keywords)
        overlap = sum(1 for w in title_words if w in paper_text)
        if overlap < 2 and relevance > 0.3:
            uncited_relevant.append(entry)

    if uncited_relevant:
        top_uncited = sorted(uncited_relevant, key=lambda e: e.get("relevance_score", 0), reverse=True)[:5]
        for entry in top_uncited:
            findings.append({
                "severity": "major",
                "category": "literature_coverage",
                "section": "Landasan Teori",
                "description": (
                    f"Highly relevant paper not cited: '{entry.get('title', '?')}' "
                    f"(relevance={entry.get('relevance_score', 0):.2f})"
                ),
                "suggested_fix": f"Consider citing: {entry.get('doi') or entry.get('url', 'N/A')}",
                "supporting_literature": entry.get("id", ""),
            })

    # FORWARD: Check key claims have citation support
    claim_patterns = [
        (r"studi menunjukkan|studies show|research indicates", "empirical claim"),
        (r"terbukti|proven|demonstrated", "proven claim"),
        (r"secara signifikan|significantly", "significance claim"),
        (r"lebih dari \d+%|more than \d+%", "quantitative claim"),
    ]
    for pattern, claim_type in claim_patterns:
        for match in re.finditer(pattern, paper_text):
            # Check if there's a citation within 200 chars after the claim
            start = match.start()
            context = paper_text[start:start + 200]
            if not re.search(r"\[\d+\]", context):
                # Find the section this belongs to
                section_name = "Unknown"
                char_count = 0
                for sec_name, sec_text in sections.items():
                    char_count += len(sec_text)
                    if start < char_count:
                        section_name = sec_name
                        break
                findings.append({
                    "severity": "major",
                    "category": "unsupported_claim",
                    "section": section_name,
                    "description": f"Unsupported {claim_type} near: '...{paper_text[max(0,start-30):start+60]}...'",
                    "suggested_fix": "Add citation from knowledge graph or literature.",
                })

    return findings


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------
def run(cycle: int) -> dict[str, Any]:
    """Execute structural IEEE review with bidirectional KG analysis.

    Returns summary dict for state recording.
    """
    log.info("=== Agent 2: Paper Reviewer -- Cycle %d ===", cycle)

    # Read paper
    paper_path = config.CURRENT_PAPER
    if not paper_path.exists():
        log.error("Paper not found: %s", paper_path)
        return {"error": "Paper not found", "findings": []}

    paper_text = paper_path.read_text(encoding="utf-8")
    sections = _parse_sections(paper_text)
    log.info("Parsed %d sections", len(sections))

    # Load knowledge graph
    kg = load_knowledge_graph()
    log.info("Knowledge graph: %d entries", len(kg))

    # Run all checks
    all_findings: list[dict] = []
    all_findings.extend(_check_structure(sections))
    all_findings.extend(_check_abstract(sections))
    all_findings.extend(_check_citations(paper_text, sections))
    all_findings.extend(_check_methodology(sections))
    all_findings.extend(_check_formalization(paper_text))
    all_findings.extend(_check_kg_coverage(sections, kg))

    # Sort by severity: critical > major > minor
    severity_order = {"critical": 0, "major": 1, "minor": 2}
    all_findings.sort(key=lambda f: severity_order.get(f.get("severity", "minor"), 3))

    # Generate review report
    report_path = config.STATE_DIR / f"review_report_cycle{cycle}.md"
    _write_report(all_findings, cycle, sections, report_path)

    # Summary
    severity_counts = {}
    for f in all_findings:
        sev = f.get("severity", "minor")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    summary = {
        "total_findings": len(all_findings),
        "severity_counts": severity_counts,
        "sections_analyzed": len(sections),
        "kg_entries_checked": len(kg),
        "report_path": str(report_path),
    }
    log.info("Agent 2 complete: %d findings (%s)", len(all_findings), severity_counts)
    return summary


def get_findings(cycle: int) -> list[dict]:
    """Load findings from the review report JSON sidecar."""
    json_path = config.STATE_DIR / f"review_findings_cycle{cycle}.json"
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return []


def _write_report(
    findings: list[dict],
    cycle: int,
    sections: dict[str, str],
    report_path: Path,
) -> None:
    """Write structured review report as markdown + JSON sidecar."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# IEEE Paper Review — Cycle {cycle}\n",
        f"_Generated: {now}_\n\n",
        f"**Total Findings: {len(findings)}**\n\n",
    ]

    # Group by severity
    for severity in ["critical", "major", "minor"]:
        group = [f for f in findings if f.get("severity") == severity]
        if not group:
            continue
        emoji = {"critical": "🔴", "major": "🟠", "minor": "🟡"}[severity]
        lines.append(f"## {emoji} {severity.upper()} ({len(group)})\n\n")
        for i, finding in enumerate(group, 1):
            lines.append(f"### {i}. [{finding.get('category', '')}] {finding.get('section', '')}\n")
            lines.append(f"**Issue:** {finding.get('description', '')}\n\n")
            lines.append(f"**Fix:** {finding.get('suggested_fix', '')}\n\n")
            if finding.get("supporting_literature"):
                lines.append(f"**Literature:** {finding['supporting_literature']}\n\n")
            lines.append("---\n\n")

    # Section inventory
    lines.append("## 📋 Section Inventory\n\n")
    lines.append("| Section | Word Count | Has Citations |\n")
    lines.append("|---------|-----------|---------------|\n")
    for name, text in sections.items():
        if name == "preamble":
            continue
        wc = len(text.split())
        has_cites = "YES" if re.search(r"(?:\\\[|\[)\d+(?:\\\]|\])", text) else "NO"
        lines.append(f"| {name[:50]} | {wc} | {has_cites} |\n")

    report_path.write_text("".join(lines), encoding="utf-8")

    # JSON sidecar for Agent 3 to consume
    json_path = report_path.with_name(f"review_findings_cycle{cycle}.json")
    json_path.write_text(
        json.dumps(findings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    log.info("Review report: %s", report_path)
