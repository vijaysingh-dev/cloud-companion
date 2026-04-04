from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Literal

from app.core.application import get_cli_app
from app.core.migrate import get_latest_migration_version

logger = logging.getLogger(__name__)

_app_instance = None


# =============================================================================
# Internal startup / shutdown  (both run inside the *same* event loop)
# =============================================================================


async def startup(
    require_migration: bool = True,
    neo4j_mode: Literal["async", "sync"] = "async",
) -> None:
    global _app_instance
    _app_instance = get_cli_app(neo4j_mode=neo4j_mode)
    await _app_instance.start()
    if require_migration:
        version = await get_latest_migration_version(_app_instance.neo4j)
        if not version:
            raise RuntimeError("Database not migrated. Run `python -m app.cli.main migrate` first.")


async def shutdown() -> None:
    global _app_instance
    if _app_instance and _app_instance.started:
        await _app_instance.stop()
    _app_instance = None


# =============================================================================
# Public entry points
# =============================================================================


def run_async(func: Callable, require_migration: bool = True) -> None:
    """
    Entry point for fully-async CLI commands.

    Lifecycle:  startup → await func() → shutdown
    Everything runs in one asyncio.run() call.
    """

    async def runner() -> None:
        await startup(require_migration=require_migration, neo4j_mode="async")
        try:
            await func()
        finally:
            await shutdown()

    asyncio.run(runner())


def run_sync(func: Callable, require_migration: bool = True) -> None:
    """
    Entry point for sync CLI commands (e.g. Cartography intel modules).

    Why one event loop?
    -------------------
    Using two separate asyncio.run() calls (one for init, one for teardown)
    destroys and recreates the event loop between them.  Any async driver
    (Neo4j AsyncDriver, aiohttp sessions, …) initialised in the first loop
    becomes invalid in the second loop, causing subtle errors on teardown or
    if anything async is touched mid-flight.

    Instead we keep a *single* long-lived loop:
        1. startup() runs in the loop (async — connects drivers).
        2. func() runs in a ThreadPoolExecutor so it can block freely without
           stalling the loop.  The loop stays alive and can service any
           async teardown callbacks.
        3. shutdown() runs in the loop (async — closes drivers cleanly).

    The Neo4jService is started with mode="sync" so that any execute_query
    call inside func() (or code it calls) uses the sync driver automatically,
    with no changes required at call sites.
    """

    async def runner() -> None:
        await startup(require_migration=require_migration, neo4j_mode="sync")
        try:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=1) as pool:
                await loop.run_in_executor(pool, func)
        finally:
            await shutdown()

    asyncio.run(runner())


# =============================================================================
# App accessor  (use inside both async and sync funcs after startup)
# =============================================================================


def get_app():
    if _app_instance is None:
        raise RuntimeError("App not initialized. Use run_async() or run_sync().")
    return _app_instance
