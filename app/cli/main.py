import typer

from app.cli.migrate import cli as migrate_cli
from app.cli.organization import cli as org_cli
from app.cli.account import cli as account_cli
from app.cli.api_key import cli as key_cli


cli = typer.Typer()

cli.add_typer(migrate_cli, name="migrate")
cli.add_typer(org_cli, name="org")
cli.add_typer(account_cli, name="account")
cli.add_typer(key_cli, name="key")

if __name__ == "__main__":
    cli()
