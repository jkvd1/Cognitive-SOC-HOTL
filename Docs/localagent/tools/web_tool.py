"""HTTP request tool with domain allowlist enforcement."""
from __future__ import annotations

from urllib.parse import urlparse

import httpx

import config


def web_request(
    url: str,
    method: str = "GET",
    body: str | None = None,
    headers: dict | None = None,
) -> str:
    """Make an HTTP GET/POST request to an allowlisted domain."""
    # --- Domain allowlist check ---
    parsed = urlparse(url)
    domain = parsed.netloc.lower().lstrip("www.")
    if not any(domain == d or domain.endswith("." + d) for d in config.ALLOWED_DOMAINS):
        raise PermissionError(
            f"Domain not allowlisted: {domain!r}. "
            f"Allowed: {config.ALLOWED_DOMAINS}"
        )

    method = method.upper()
    if method not in {"GET", "POST"}:
        return f"[ERROR] Unsupported method: {method!r}"

    safe_headers = headers or {}
    # Strip authorization headers if not to telegram
    if "api.telegram.org" not in domain:
        safe_headers = {
            k: v for k, v in safe_headers.items()
            if k.lower() not in {"authorization", "cookie"}
        }

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            if method == "GET":
                resp = client.get(url, headers=safe_headers)
            else:
                resp = client.post(url, content=body or "", headers=safe_headers)

        body_text = resp.text[: config.MAX_WEB_RESPONSE_BYTES]
        return (
            f"[HTTP {resp.status_code}]\n"
            f"Content-Type: {resp.headers.get('content-type', 'unknown')}\n\n"
            f"{body_text}"
        )
    except httpx.TimeoutException:
        return "[ERROR] Request timed out after 15s."
    except Exception as exc:
        return f"[ERROR] {type(exc).__name__}: {exc}"
