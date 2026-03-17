import typer
from rich import print
from typing import Annotated

from app.core.constants import CloudProviderEnum
from app.models.graph import Account
from app.cli.runtime import run_async, get_app


cli = typer.Typer()


@cli.command()
def create(
    org_name: str,
    name: str,
    provider: Annotated[CloudProviderEnum, typer.Argument(help="Cloud provider (aws, azure, gcp)")],
    account_id: str,
):
    async def _create():
        app = get_app()

        org = await app.repo.organization.get_org_by_name(org_name)
        if not org:
            print(f"[red]Error:[/red] Organization '[bold]{org_name}[/bold]' not found.")
            raise typer.Exit(code=1)

        acc = Account(
            org_id=org.id,
            name=name,
            provider=provider,
            account_id=account_id,
        )

        await app.repo.organization.create_account(acc)
        print(f"[green]Cloud account created for [bold]{provider.value}[/bold][/green]")

    run_async(_create)


@cli.command()
def list(org_id: str):
    async def _list():
        app = get_app()

        accounts = await app.repo.organization.list_accounts(org_id)
        for r in accounts:
            print(f"{r.account_id} | {r.name} | [bold cyan]{r.provider.value}[/bold cyan]")

    run_async(_list)
