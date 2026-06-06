"""RSS/Atom feed fetcher with keyword filtering."""
from __future__ import annotations

from urllib.parse import urlparse

import config

try:
    import feedparser
    _HAS_FP = True
except ImportError:
    _HAS_FP = False


def rss_fetch(
    url: str | None = None,
    keyword_filter: str | None = None,
    max_entries: int = 10,
) -> str:
    if not _HAS_FP:
        return "[ERROR] feedparser not installed."

    feeds_to_fetch: list[str] = []
    if url:
        feeds_to_fetch.append(url)
    else:
        feeds_to_fetch = config.RSS_FEEDS

    if not feeds_to_fetch:
        return "[ERROR] No RSS feed URL provided and RSS_FEEDS env var is empty."

    # Allowlist check for explicit URLs
    if url:
        domain = urlparse(url).netloc.lower().lstrip("www.")
        if config.ALLOWED_DOMAINS and not any(
            domain == d or domain.endswith("." + d) for d in config.ALLOWED_DOMAINS
        ):
            raise PermissionError(f"RSS domain not allowlisted: {domain!r}")

    kw_lower = keyword_filter.lower() if keyword_filter else None
    results: list[str] = []

    for feed_url in feeds_to_fetch:
        try:
            feed = feedparser.parse(feed_url)
            feed_title = feed.feed.get("title", feed_url)
            results.append(f"\n📡 **{feed_title}**")
            count = 0
            for entry in feed.entries:
                if count >= max_entries:
                    break
                title = entry.get("title", "(no title)")
                link = entry.get("link", "")
                summary = entry.get("summary", "")[:200]
                # Keyword filter
                if kw_lower:
                    combined = f"{title} {summary}".lower()
                    if kw_lower not in combined:
                        continue
                results.append(f"  • {title}\n    {link}\n    {summary}")
                count += 1
        except Exception as exc:
            results.append(f"  [ERROR fetching {feed_url}]: {exc}")

    if not results:
        return "No RSS entries found."
    return "\n".join(results)
