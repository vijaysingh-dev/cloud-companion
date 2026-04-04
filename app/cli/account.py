from rich import print

import typer
from app.cli.runtime import run_async, get_app

from app.core.constants import CloudProviderEnum
from app.models.graph import Account


cli = typer.Typer(no_args_is_help=True)


@cli.command()
def create(
    provider: CloudProviderEnum = typer.Option(
        ..., "--provider", "-p", help="Cloud provider (aws, azure, gcp)"
    ),
    org_name: str = typer.Option(..., "--org-name", "-o", help="Organization name"),
    name: str = typer.Option(..., "--name", "-n", help="Account name"),
    account_id: str = typer.Option(..., "--account-id", "-a", help="Cloud account ID"),
):
    async def _create():
        app = get_app()

        org = await app.repo.organization.get_org_by_name(org_name)
        if not org:
            print(f"[red]Error:[/red] Organization '[bold]{org_name}[/bold]' not found.")
            raise typer.Exit(code=1)

        acc = Account(
            id=account_id,
            org_id=org.id,
            name=name,
            provider=provider,
        )

        await app.repo.account.create_account(acc)
        print(f"[green]Cloud account created for [bold]{provider.value}[/bold][/green]")

    run_async(_create)


@cli.command()
def list(org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID")):
    async def _list():
        app = get_app()

        accounts = await app.repo.account.list_accounts(org_id)
        for r in accounts:
            print(f"{r.id} | {r.name} | [bold cyan]{r.provider.value}[/bold cyan]")

    run_async(_list)
