import secrets
from rich import print
from datetime import datetime, timezone, timedelta

import typer
from app.cli.runtime import run_async, get_app

from app.models.graph import APIKey
from app.api.deps import hash_api_key


cli = typer.Typer(no_args_is_help=True)


@cli.command()
def create(
    org_name: str = typer.Option(..., "--org-name", "-o", help="Organization name"),
    name: str = typer.Option(..., "--name", "-n", help="API key name"),
    days_valid: int = typer.Option(30, "--days-valid", "-d", help="Days until key expires"),
):
    async def _create():
        app = get_app()

        org = await app.repo.organization.get_org_by_name(org_name)
        if not org:
            print(f"[red]Error:[/red] Organization '[bold]{org_name}[/bold]' not found.")
            raise typer.Exit(code=1)

        raw_key = "cc_live_" + secrets.token_hex(32)
        expires = datetime.now(timezone.utc) + timedelta(days=days_valid)
        key_data = APIKey(
            org_id=org.id,
            name=name,
            hashed_key=hash_api_key(raw_key),
            expires_at=expires.isoformat(),
        )

        await app.repo.api_key.create_api_key(key_data)

        print("\n[green]✔ API Key created successfully[/green]")
        print(f"Organization: [cyan]{org.name}[/cyan]")
        print(f"Name:         {name}")
        print(f"Key:          [bold yellow]{raw_key}[/bold yellow]")
        print(f"Expires at:   {expires.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("\n[dim]Note: Store this key safely. It will not be shown again.[/dim]")

    run_async(_create)


@cli.command()
def revoke(key_id: str = typer.Option(..., "--key-id", "-k", help="API key ID")):
    async def _revoke():
        app = get_app()

        await app.repo.api_key.revoke_api_key(key_id)
        print("[yellow]Key revoked[/yellow]")

    run_async(_revoke)


@cli.command()
def list(org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID")):
    async def _list():
        app = get_app()

        keys = await app.repo.api_key.list_api_keys(org_id)
        for r in keys:
            print(f"{r.id} | {r.name} | Active: {r.is_active}")

    run_async(_list)
