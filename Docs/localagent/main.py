"""Entry point — bootstraps runtime, channel, and scheduler as concurrent tasks."""
from __future__ import annotations

import asyncio
import logging
import sys

import config
from channel.telegram import TelegramChannel
from runtime import AgentRuntime
from scheduler import Scheduler
from state import StateManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


async def _channel_loop(channel: TelegramChannel, state: StateManager) -> None:
    """Continuously poll Telegram and push tasks to the queue."""
    log.info("Telegram channel polling started.")
    while True:
        task = await channel.poll()
        if task is not None:
            await state.enqueue(task)


async def main() -> None:
    # Validate critical config
    if not config.TELEGRAM_TOKEN:
        log.error("TELEGRAM_TOKEN is not set. Exiting.")
        sys.exit(1)
    if not config.ALLOWED_CHAT_IDS:
        log.warning("ALLOWED_CHAT_IDS is empty — no messages will be accepted.")

    config.ensure_dirs()
    log.info(
        "Starting LocalAgent | model=%s | workspace=%s",
        config.OLLAMA_MODEL,
        config.WORKSPACE_ROOT,
    )

    state = StateManager()
    channel = TelegramChannel()
    runtime = AgentRuntime(state, channel)
    scheduler = Scheduler(channel, state)

    try:
        await asyncio.gather(
            _channel_loop(channel, state),
            runtime.run(),
            scheduler.run(),
        )
    except asyncio.CancelledError:
        log.info("Shutdown signal received.")
    finally:
        await channel.close()
        log.info("LocalAgent stopped.")


if __name__ == "__main__":
    asyncio.run(main())
