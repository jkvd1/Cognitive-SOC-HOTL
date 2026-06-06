"""Ollama inference client with MCP tool-call parsing and retry logic."""
import json
import logging
import re
import time
from typing import Any

import httpx

import config

log = logging.getLogger(__name__)

# Ollama API endpoint
_CHAT_URL = f"{config.OLLAMA_BASE_URL}/api/chat"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
class ToolCall:
    __slots__ = ("name", "arguments")

    def __init__(self, name: str, arguments: dict) -> None:
        self.name = name
        self.arguments = arguments

    def __repr__(self) -> str:
        return f"ToolCall(name={self.name!r}, args={self.arguments})"


class InferenceResult:
    __slots__ = ("content", "tool_calls", "raw")

    def __init__(
        self,
        content: str,
        tool_calls: list[ToolCall],
        raw: dict,
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls
        self.raw = raw


# ---------------------------------------------------------------------------
# Core inference function
# ---------------------------------------------------------------------------
def infer(
    messages: list[dict],
    tools: list[dict] | None = None,
) -> InferenceResult:
    """Send messages to Ollama and return structured result.

    Retries up to 3 times with exponential backoff.
    Falls back to regex JSON extraction if tool_calls not in response.
    """
    payload: dict[str, Any] = {
        "model": config.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            with httpx.Client(timeout=config.OLLAMA_TIMEOUT) as client:
                resp = client.post(_CHAT_URL, json=payload)
                resp.raise_for_status()
                body = resp.json()
                return _parse_response(body)
        except Exception as exc:
            last_exc = exc
            wait = 2 ** attempt
            log.warning("Ollama attempt %d failed: %s — retrying in %ds", attempt + 1, exc, wait)
            time.sleep(wait)

    raise RuntimeError(f"Ollama unreachable after 3 attempts: {last_exc}") from last_exc


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------
def _parse_response(body: dict) -> InferenceResult:
    msg: dict = body.get("message", {})
    content: str = msg.get("content") or ""
    raw_calls: list[dict] = msg.get("tool_calls") or []

    tool_calls: list[ToolCall] = []

    # --- Primary: Ollama native tool_calls format ---
    for tc in raw_calls:
        fn = tc.get("function", {})
        name = fn.get("name", "")
        args = fn.get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        if name:
            tool_calls.append(ToolCall(name=name, arguments=args))

    # --- Fallback: extract JSON tool calls from content text ---
    if not tool_calls and content:
        tool_calls = _extract_tool_calls_from_text(content)

    return InferenceResult(content=content, tool_calls=tool_calls, raw=body)


# Regex to find JSON blocks that look like tool calls in model text output
_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_TOOL_CALL_RE = re.compile(
    r'"(?:tool|function|name)"\s*:\s*"([^"]+)".*?"(?:arguments?|params?|input)"\s*:\s*(\{[^}]*\})',
    re.DOTALL,
)


def _extract_tool_calls_from_text(text: str) -> list[ToolCall]:
    """Best-effort extraction of tool-call JSON from model text output."""
    calls: list[ToolCall] = []
    # Try JSON fenced blocks first
    for match in _JSON_BLOCK_RE.finditer(text):
        try:
            obj = json.loads(match.group(1))
            name = obj.get("name") or obj.get("tool") or obj.get("function")
            args = obj.get("arguments") or obj.get("params") or obj.get("input") or {}
            if name:
                calls.append(ToolCall(name=name, arguments=args))
        except (json.JSONDecodeError, AttributeError):
            continue
    # Inline pattern fallback
    if not calls:
        for match in _TOOL_CALL_RE.finditer(text):
            try:
                name = match.group(1)
                args = json.loads(match.group(2))
                calls.append(ToolCall(name=name, arguments=args))
            except (json.JSONDecodeError, IndexError):
                continue
    return calls
