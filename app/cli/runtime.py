# app/cli/runtime.py

import asyncio
from app.core.application import get_cli_app
from app.core.migrate import get_latest_migration_version

_app_instance = None


async def startup(require_migration: bool = True):
    global _app_instance
    _app_instance = get_cli_app()
    await _app_instance.start()
    if require_migration:
        version = await get_latest_migration_version(_app_instance.neo4j)
        if not version:
            raise RuntimeError("Database not migrated. Run `python -m app.cli.main migrate` first.")


async def shutdown():
    global _app_instance
    if _app_instance and _app_instance.started:
        await _app_instance.stop()
    _app_instance = None


def run_async(func, require_migration: bool = True):
    async def runner():
        await startup(require_migration)
        try:
            await func()
        finally:
            await shutdown()

    asyncio.run(runner())


def get_app():
    if _app_instance is None:
        raise RuntimeError("App not initialized. Use run_async() or run_sync().")
    return _app_instance
