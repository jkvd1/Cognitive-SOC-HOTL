"""Core agent runtime — seven-stage agentic loop with ReAct tool execution."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import config
import llm
import mcp.schema as mcp_schema
from state import AgentState, StateManager, Task
from tools.router import dispatch

log = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a personal AI assistant running locally on the user's machine.
You have access to tools for managing files, running code, searching notes, managing tasks,
checking calendars, fetching RSS feeds, and making HTTP requests.

RULES:
- Always use tools when the user's request requires reading/writing files or data.
- After tool results are available, synthesize a clear, concise final answer.
- Never fabricate file contents or tool outputs.
- Be proactive: if you notice tasks are overdue or deadlines are near, mention it.
- Keep responses focused and actionable.
Current time: {timestamp}
Workspace: /workspace
"""


class AgentRuntime:
    def __init__(self, state: StateManager, channel) -> None:
        self._state = state
        self._channel = channel
        self._tools = mcp_schema.get_all()

    async def run(self) -> None:
        """Main event loop — consume tasks from queue."""
        log.info("Agent runtime started.")
        while True:
            task: Task = await self._state.dequeue()
            try:
                await self._process(task)
            except Exception as exc:
                log.exception("Unhandled error processing task %s: %s", task.task_id, exc)
                await self._channel.send(
                    task.reply_to,
                    f"⚠️ Internal error: `{type(exc).__name__}: {exc}`"
                )
            finally:
                self._state.transition(AgentState.IDLE)

    async def _process(self, task: Task) -> None:
        """Execute one full agentic cycle for *task*."""
        # ── RECEIVING ──────────────────────────────────────────────────────
        self._state.transition(AgentState.RECEIVING)
        self._state.record_activity(task.session_id)

        messages: list[dict] = self._state.load_session(task.session_id)
        if not messages:
            messages.append({
                "role": "system",
                "content": _SYSTEM_PROMPT.format(
                    timestamp=datetime.now(timezone.utc).isoformat()
                ),
            })
        messages.append({"role": "user", "content": task.message})

        await self._channel.send_typing(task.reply_to)

        # ── PLANNING + EXECUTING (ReAct loop) ─────────────────────────────
        self._state.transition(AgentState.PLANNING)

        for round_num in range(config.MAX_TOOL_ROUNDS):
            # Run inference (sync, offloaded to thread pool)
            result = await asyncio.get_event_loop().run_in_executor(
                None, llm.infer, messages, self._tools
            )

            if not result.tool_calls:
                # No more tool calls — final answer ready
                break

            # ── EXECUTING ────────────────────────────────────────────────
            self._state.transition(AgentState.EXECUTING)
            log.info(
                "Round %d: executing %d tool(s): %s",
                round_num + 1,
                len(result.tool_calls),
                [tc.name for tc in result.tool_calls],
            )

            # Append assistant tool-call request to history
            messages.append({
                "role": "assistant",
                "content": result.content or "",
            })

            # Execute each tool and collect results
            for tc in result.tool_calls:
                await self._channel.send_typing(task.reply_to)
                tool_result = dispatch(tc.name, tc.arguments)
                log.debug("Tool %r → is_error=%s", tc.name, tool_result.is_error)
                messages.append(tool_result.to_message())

            # Back to planning for next inference round
            self._state.transition(AgentState.PLANNING)

        # ── RESPONDING ────────────────────────────────────────────────────
        self._state.transition(AgentState.RESPONDING)

        final_content = result.content if result.tool_calls == [] else result.content
        if not final_content:
            # Get a clean summary if the last inference only triggered tools
            summary_result = await asyncio.get_event_loop().run_in_executor(
                None, llm.infer, messages, None
            )
            final_content = summary_result.content

        if final_content:
            messages.append({"role": "assistant", "content": final_content})
            self._state.save_session(task.session_id, messages)
            await self._channel.send(task.reply_to, final_content)
        else:
            err_msg = "⚠️ No response generated. Please try again."
            await self._channel.send(task.reply_to, err_msg)
            log.warning("Empty response for task %s", task.task_id)
