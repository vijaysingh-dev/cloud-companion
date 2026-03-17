import asyncio

from app.core.application import Application
from app.core.migrate import get_latest_migration_version


_app_instance = Application()


async def startup(require_migration: bool = True):
    await _app_instance.start()

    if require_migration:
        version = await get_latest_migration_version(_app_instance.neo4j)
        if not version:
            raise RuntimeError("Database not migrated. Run `python -m app.cli.main migrate` first.")


async def shutdown():
    await _app_instance.stop()


def run_async(func, require_migration: bool = True):
    async def runner():
        await startup(require_migration)
        try:
            await func()
        finally:
            await shutdown()

    asyncio.run(runner())


def get_app():
    return _app_instance
