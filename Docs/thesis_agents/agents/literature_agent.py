"""Agent 1 — Literature Scholar.

Searches IEEE Xplore, Google Scholar, and Semantic Scholar for papers
relevant to the thesis. Builds a bidirectional knowledge graph.
No API keys required — uses free web endpoints and scraping.
"""
import json
import logging
import random
import re
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

import config
from pipeline_state import load_knowledge_graph, save_knowledge_graph

log = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"


# ---------------------------------------------------------------------------
# Search backends
# ---------------------------------------------------------------------------
def _search_semantic_scholar(query: str, limit: int = 5) -> list[dict]:
    """Search Semantic Scholar (free, no key, rate-limited to 100 req/5min)."""
    results: list[dict] = []
    try:
        resp = requests.get(
            _SEMANTIC_SCHOLAR_API,
            params={
                "query": query,
                "limit": limit,
                "fields": "title,authors,year,abstract,citationCount,url,externalIds",
            },
            headers=_HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            for paper in data.get("data", []):
                doi = ""
                ext = paper.get("externalIds") or {}
                if isinstance(ext, dict):
                    doi = ext.get("DOI", "")
                authors_list = paper.get("authors") or []
                author_str = ", ".join(
                    a.get("name", "") for a in authors_list[:4]
                )
                if len(authors_list) > 4:
                    author_str += " et al."
                results.append({
                    "title": paper.get("title", ""),
                    "authors": author_str,
                    "year": paper.get("year"),
                    "abstract": (paper.get("abstract") or "")[:500],
                    "citations": paper.get("citationCount", 0),
                    "doi": doi,
                    "url": paper.get("url", ""),
                    "source": "Semantic Scholar",
                })
        else:
            log.warning("Semantic Scholar returned %d for: %s", resp.status_code, query)
    except Exception as exc:
        log.warning("Semantic Scholar search failed: %s", exc)
    return results


def _search_google_scholar_scrape(query: str, limit: int = 5) -> list[dict]:
    """Scrape Google Scholar results (fallback, may be rate-limited)."""
    results: list[dict] = []
    url = f"https://scholar.google.com/scholar?q={quote_plus(query)}&hl=en"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            log.warning("Google Scholar returned %d", resp.status_code)
            return results
        soup = BeautifulSoup(resp.text, "html.parser")
        for item in soup.select(".gs_r.gs_or.gs_scl")[:limit]:
            title_el = item.select_one(".gs_rt a")
            title = title_el.get_text(strip=True) if title_el else ""
            link = title_el["href"] if title_el and title_el.has_attr("href") else ""
            author_el = item.select_one(".gs_a")
            author_text = author_el.get_text(strip=True) if author_el else ""
            snippet_el = item.select_one(".gs_rs")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            # Parse year from author line
            year_match = re.search(r"\b(20\d{2})\b", author_text)
            year = int(year_match.group(1)) if year_match else None
            # Parse citation count
            cite_el = item.select_one('a[href*="cites"]')
            cite_count = 0
            if cite_el:
                cite_match = re.search(r"(\d+)", cite_el.get_text())
                if cite_match:
                    cite_count = int(cite_match.group(1))
            results.append({
                "title": title,
                "authors": author_text.split(" - ")[0] if " - " in author_text else author_text,
                "year": year,
                "abstract": snippet[:500],
                "citations": cite_count,
                "doi": "",
                "url": link,
                "source": "Google Scholar",
            })
    except Exception as exc:
        log.warning("Google Scholar scrape failed: %s", exc)
    return results


# ---------------------------------------------------------------------------
# Knowledge graph operations
# ---------------------------------------------------------------------------
def _deduplicate(existing: list[dict], new_entries: list[dict]) -> list[dict]:
    """Deduplicate by normalized title."""
    seen_titles: set[str] = set()
    for entry in existing:
        norm = entry.get("title", "").lower().strip()
        if norm:
            seen_titles.add(norm)

    unique: list[dict] = []
    for entry in new_entries:
        norm = entry.get("title", "").lower().strip()
        if norm and norm not in seen_titles:
            seen_titles.add(norm)
            unique.append(entry)
    return unique


def _compute_relevance(entry: dict, paper_text: str) -> float:
    """Score 0-1: how relevant an entry is to the thesis paper."""
    score = 0.0
    title = (entry.get("title") or "").lower()
    abstract = (entry.get("abstract") or "").lower()
    combined = title + " " + abstract

    # Keyword matching against thesis topics
    keywords = [
        ("cognitive soc", 0.15), ("soar", 0.10), ("security operations", 0.10),
        ("threat intelligence", 0.10), ("human-on-the-loop", 0.15),
        ("human-in-the-loop", 0.08), ("agentic ai", 0.12),
        ("random forest", 0.08), ("intrusion detection", 0.08),
        ("concept drift", 0.10), ("feedback loop", 0.08),
        ("mttr", 0.08), ("siem", 0.06), ("wazuh", 0.06),
        ("orchestration", 0.06), ("automation", 0.05),
        ("false positive", 0.06), ("alert fatigue", 0.08),
    ]
    for kw, weight in keywords:
        if kw in combined:
            score += weight

    # Recency bonus
    year = entry.get("year")
    if year and year >= 2024:
        score += 0.10
    elif year and year >= 2022:
        score += 0.05

    # Citation strength
    cites = entry.get("citations", 0)
    if cites > 50:
        score += 0.10
    elif cites > 10:
        score += 0.05

    return min(score, 1.0)


def _build_connections(entries: list[dict]) -> None:
    """Build bidirectional connections based on keyword overlap."""
    for i, entry_a in enumerate(entries):
        words_a = set(re.findall(r"\w{4,}", (
            (entry_a.get("title") or "") + " " +
            (entry_a.get("abstract") or "")
        ).lower()))
        connections: list[str] = []
        for j, entry_b in enumerate(entries):
            if i == j:
                continue
            words_b = set(re.findall(r"\w{4,}", (
                (entry_b.get("title") or "") + " " +
                (entry_b.get("abstract") or "")
            ).lower()))
            overlap = len(words_a & words_b)
            if overlap >= 5:
                connections.append(entry_b.get("id", f"LIT-{j+1:03d}"))
        entry_a["connections"] = connections[:10]


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------
def run(cycle: int) -> dict[str, Any]:
    """Execute literature search and knowledge graph update.

    Returns summary dict for state recording.
    """
    log.info("=== Agent 1: Literature Scholar -- Cycle %d ===", cycle)

    # Load existing knowledge graph
    existing_kg = load_knowledge_graph()
    log.info("Existing KG entries: %d", len(existing_kg))

    # Read current paper for relevance scoring
    paper_text = ""
    if config.CURRENT_PAPER.exists():
        paper_text = config.CURRENT_PAPER.read_text(encoding="utf-8").lower()

    # Select search topics (rotate through them across cycles)
    topics = config.SEARCH_TOPICS
    # Use 3 topics per cycle, rotating
    start_idx = ((cycle - 1) * 3) % len(topics)
    selected_topics = [topics[(start_idx + i) % len(topics)] for i in range(3)]
    log.info("Search topics: %s", selected_topics)

    # Search across backends
    all_results: list[dict] = []
    for topic in selected_topics:
        # Primary: Semantic Scholar (free API)
        results = _search_semantic_scholar(topic, limit=5)
        all_results.extend(results)
        time.sleep(1 + random.random())  # Rate limit courtesy

        # Fallback: Google Scholar scrape
        if len(results) < 3:
            gs_results = _search_google_scholar_scrape(topic, limit=3)
            all_results.extend(gs_results)
            time.sleep(2 + random.random())

    log.info("Raw search results: %d", len(all_results))

    # Deduplicate against existing KG
    unique = _deduplicate(existing_kg, all_results)
    log.info("New unique entries: %d", len(unique))

    # Score relevance and filter
    for entry in unique:
        entry["relevance_score"] = round(_compute_relevance(entry, paper_text), 3)

    # Keep only relevant entries (score > 0.15)
    relevant = [e for e in unique if e["relevance_score"] > 0.15]
    relevant.sort(key=lambda e: e["relevance_score"], reverse=True)
    relevant = relevant[:config.MAX_LITERATURE_ENTRIES_PER_CYCLE]
    log.info("Relevant new entries: %d", len(relevant))

    # Assign IDs and metadata
    next_id = len(existing_kg) + 1
    for entry in relevant:
        entry["id"] = f"LIT-{next_id:03d}"
        entry["added_cycle"] = cycle
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["connections"] = []
        next_id += 1

    # Merge with existing KG
    merged_kg = existing_kg + relevant

    # Build bidirectional connections across all entries
    _build_connections(merged_kg)

    # Save
    save_knowledge_graph(merged_kg)
    log.info("Knowledge graph total: %d entries", len(merged_kg))

    # Also append human-readable summary to literature_insights.md
    if relevant:
        _append_insights(relevant, cycle)

    summary = {
        "topics_searched": selected_topics,
        "raw_results": len(all_results),
        "new_entries": len(relevant),
        "total_kg_entries": len(merged_kg),
        "top_entry": relevant[0]["title"] if relevant else "none",
    }
    log.info("Agent 1 complete: %s", json.dumps(summary, indent=2))
    return summary


def _append_insights(entries: list[dict], cycle: int) -> None:
    """Append new literature findings to literature_insights.md."""
    lines = [
        f"\n\n---\n\n## Cycle {cycle} — New Literature Findings\n",
        f"_Added: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n\n",
    ]
    for entry in entries:
        lines.append(f"### {entry.get('title', 'Untitled')}\n")
        lines.append(f"- **Authors:** {entry.get('authors', 'N/A')}\n")
        lines.append(f"- **Year:** {entry.get('year', 'N/A')}\n")
        lines.append(f"- **Source:** {entry.get('source', 'N/A')}\n")
        if entry.get("doi"):
            lines.append(f"- **DOI:** {entry['doi']}\n")
        lines.append(f"- **Relevance:** {entry.get('relevance_score', 0):.2f}\n")
        if entry.get("abstract"):
            lines.append(f"- **Key findings:** {entry['abstract'][:300]}...\n")
        if entry.get("connections"):
            lines.append(f"- **Connected to:** {', '.join(entry['connections'])}\n")
        lines.append("\n")

    insights_path = config.LITERATURE_INSIGHTS
    with open(insights_path, "a", encoding="utf-8") as f:
        f.writelines(lines)
    log.info("Appended %d entries to %s", len(entries), insights_path.name)
