from rich import print

import typer
from app.cli.runtime import run_async, get_app

from app.models.graph import Organization


cli = typer.Typer(no_args_is_help=True)


@cli.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Organization name"),
    description: str = typer.Option("", "--description", "-d", help="Organization description"),
):
    async def _create():
        app = get_app()

        org = Organization(name=name, description=description)
        await app.repo.organization.create_org(org)
        print(f"[green]Organization created[/green] ID: {org.id}")

    run_async(_create)


@cli.command()
def list():
    async def _list():
        app = get_app()

        orgs = await app.repo.organization.list_organizations()
        for r in orgs:
            print(f"{r.id} | {r.name}")

    run_async(_list)


@cli.command()
def delete(org_id: str = typer.Option(..., "--org-id", "-i", help="Organization ID")):
    async def _delete():
        app = get_app()

        await app.repo.organization.delete_org(org_id)
        print("[red]Organization deleted[/red]")

    run_async(_delete)
