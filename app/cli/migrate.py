import typer
from app.cli.runtime import run_async, get_app

from app.core.migrate import run_migrations


cli = typer.Typer(invoke_without_command=True)


@cli.callback()
def migrate(ctx: typer.Context):
    async def _migrate():
        app = get_app()
        await run_migrations(app.neo4j)
        print("Migrations applied successfully.")

    run_async(_migrate, require_migration=False)
