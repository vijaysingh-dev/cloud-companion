import logging
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from app.core.config import settings
from app.core.constants import CloudProviderEnum
from app.core.validators import normalize_region

from app.services.cartography_companion.redis_tracker import RedisSyncTracker
from app.services.cartography_companion.pipeline import Pipeline, SyncResult
from app.services.cartography_companion.registry.service_registry import registry
from app.cli.runtime import get_app, run_async


logger = logging.getLogger(__name__)

console = Console()

cli = typer.Typer(no_args_is_help=True)

# ---------------------------------------------------------------------------
# sync utils
# ---------------------------------------------------------------------------


def _normalize_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _print_result(result: SyncResult) -> None:
    console.print()

    table = Table(title="Sync summary", show_lines=False, box=box.SIMPLE)
    table.add_column("Service", style="cyan", min_width=35)
    table.add_column("Result", min_width=12)
    table.add_column("Detail", style="dim")

    for key in result.succeeded:
        table.add_row(key, "[green]ok[/green]", "")

    for key, reason in result.skipped.items():
        table.add_row(key, "[yellow]skipped[/yellow]", reason)

    for key in result.invalid:
        # Show just the first sentence — omit the long "Available: [...]" list
        short = result.failed[key].split(".")[0]
        table.add_row(key, "[dim]invalid[/dim]", short)

    for key, err in result.runtime_failures.items():
        table.add_row(key, "[red]failed[/red]", err[:80])

    console.print(table)

    if result.all_ok:
        console.print("[green]All services completed successfully.[/green]")
    else:
        counts = []
        if result.runtime_failures:
            counts.append(f"[red]{len(result.runtime_failures)} failed[/red]")
        if result.invalid:
            counts.append(f"[dim]{len(result.invalid)} invalid[/dim]")
        if result.skipped:
            counts.append(f"[yellow]{len(result.skipped)} skipped[/yellow]")
        console.print("  ".join(counts))


@cli.command("run")
def sync_run(
    provider: CloudProviderEnum = typer.Option(
        ...,
        "--provider",
        "-p",
        help="Cloud provider (aws, azure, gcp)",
    ),
    account_id: str = typer.Option(..., "--account-id", "-a", help="Cloud account ID"),
    region: str = typer.Option(..., "--regions", "-r", help="Comma-separated regions to sync"),
    service: str = typer.Option(..., "--services", "-s", help="Comma-separated service(s) to sync"),
    force: bool = typer.Option(False, "--force", help="Ignore existing locks"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without running"),
):
    """
    Selectively sync one or more cloud services into the graph.

    \b
    Examples:
      sync run -a 123456789012 -r us-east-1 -s ec2:instance
      sync run -a 123456789012 -s s3,iam
      sync run -a 123456789012 -p azure -s compute,resource_groups
      sync run -a 123456789012 -p gcp -s bigquery,bigquery_connection --dry-run
    """
    regions = normalize_region(provider, region)
    services = _normalize_list(service)

    # expand() never raises — errors come back in the dict
    ordered, expand_errors = registry.expand(services, provider=provider.value)

    # ── Plan table ───────────────────────────────────────────────────────
    table = Table(title=f"Sync plan — {account_id} ({provider.value})", show_lines=False)
    table.add_column("Order", style="dim", width=6)
    table.add_column("Service", style="cyan")
    table.add_column("Scope", style="dim")
    table.add_column("Depends on", style="dim")
    table.add_column("Note", style="dim")

    for i, svc in enumerate(ordered, 1):
        scope = ", ".join(regions) if svc.requires_region else "global"
        deps = ", ".join(svc.depends_on) if svc.depends_on else "—"
        table.add_row(str(i), svc.key, scope, deps, "")

    # Invalid keys shown at the bottom of the plan, unordered
    for key, reason in expand_errors.items():
        # Show only the first sentence (omits the long available list)
        short = reason.split(".")[0]
        table.add_row("—", f"[dim]{key}[/dim]", "—", "—", f"[red]{short}[/red]")

    console.print(table)

    if not ordered:
        console.print("[red]No valid services to sync.[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        if expand_errors:
            console.print(
                f"\n[yellow][dry-run][/yellow] "
                f"[red]{len(expand_errors)} invalid service(s) would be skipped.[/red]"
            )
        console.print("\n[yellow][dry-run] No sync performed.[/yellow]")
        raise typer.Exit()

    async def _run():
        app = get_app()
        pipeline = Pipeline(app.neo4j, app.redis)
        result = await pipeline.run(
            account_id=account_id,
            provider=provider,
            service_keys=services,
            regions=regions,
            force=force,
        )
        _print_result(result)
        if not result.all_ok:
            raise typer.Exit(code=1)

    run_async(_run)


@cli.command("status")
def sync_status(
    provider: CloudProviderEnum = typer.Option(
        ...,
        "--provider",
        "-p",
        help="Cloud provider (aws, azure, gcp)",
    ),
    account_id: str = typer.Option(..., "--account-id", "-a", help="Cloud account ID"),
    stale_hours: int = typer.Option(
        24, "--stale-hours", help="Flag services not synced within N hours"
    ),
):
    """Show last sync status for all services on an account."""

    async def _run():
        app = get_app()

        # Neo4j: permanent completed/failed records
        statuses = await app.repo.sync.get_service_statuses(account_id)
        statuses = [s for s in statuses if s.get("provider") == provider.value]

        stale = await app.repo.sync.get_stale_services(account_id, max_age_hours=stale_hours)
        stale = [s for s in stale if s.get("provider") == provider.value]
        stale_keys = {s["service_key"] for s in stale}

        # Redis: live state for services not yet in Neo4j (running, invalid)
        known_keys = {s["service_key"] for s in statuses}
        all_keys = registry.available_keys(provider.value)
        redis_tracker = RedisSyncTracker(app.redis)
        redis_statuses = await redis_tracker.get_statuses(account_id, all_keys)

        # Merge Redis-only entries (running/invalid never reach Neo4j)
        for key, state in redis_statuses.items():
            if key not in known_keys and state.get("status") in ("invalid", "running"):
                statuses.append(
                    {
                        "service_key": key,
                        "status": state["status"],
                        "last_completed_at": state.get("updated_at", "—"),
                        "regions": [],
                        "provider": provider.value,
                        "error": state.get("error", ""),
                        "_live": True,
                    }
                )

        if not statuses:
            console.print(
                f"[yellow]No sync records found for account {account_id} "
                f"({provider.value})[/yellow]"
            )
            raise typer.Exit()

        table = Table(title=f"Sync status — {account_id} ({provider.value})", show_lines=False)
        table.add_column("Service", style="cyan", min_width=35)
        table.add_column("Status", min_width=12)
        table.add_column("Last completed", min_width=28)
        table.add_column("Regions", style="dim")
        table.add_column("Note", style="dim")

        for r in statuses:
            svc_key = r.get("service_key", "?")
            status = r.get("status", "?")
            completed = r.get("last_completed_at", "never")
            regions_str = ", ".join(r.get("regions") or ["global"])
            note = r.get("_error", "")[:60] if r.get("_from_redis") else ""

            if status == "completed":
                status_str = (
                    "[yellow]stale[/yellow]" if svc_key in stale_keys else "[green]ok[/green]"
                )
            elif status == "running":
                status_str = "[blue]running[/blue]"
            elif status == "failed":
                status_str = "[red]failed[/red]"
            elif status == "invalid":
                status_str = "[dim]invalid[/dim]"
            else:
                status_str = f"[dim]{status}[/dim]"

            table.add_row(svc_key, status_str, completed, regions_str, note)

        console.print(table)

    run_async(_run)


# ---------------------------------------------------------------------------
# sync list  (no I/O — no app needed)
# ---------------------------------------------------------------------------


@cli.command("list")
def list_services(
    provider: CloudProviderEnum = typer.Option(
        ...,
        "--provider",
        "-p",
        help="Cloud provider (aws, azure, gcp)",
    ),
):
    """List available services."""

    table = Table(
        title=f"Available services{' — ' + provider if provider else ''}",
        show_lines=False,
    )
    table.add_column("Key", style="cyan", min_width=38)
    table.add_column("Provider", style="dim", width=8)
    table.add_column("Global", width=7)
    table.add_column("Depends on", style="dim")

    for svc in sorted(registry.list_all(provider=provider), key=lambda s: s.key):
        deps = ", ".join(svc.depends_on) if svc.depends_on else "—"
        global_label = "[green]yes[/green]" if not svc.requires_region else ""
        table.add_row(svc.key, svc.provider, global_label, deps)

    console.print(table)


# ---------------------------------------------------------------------------
# sync stale
# ---------------------------------------------------------------------------


@cli.command("stale")
def sync_stale(
    account_id: str = typer.Option(..., "--account-id", "-a"),
    provider: CloudProviderEnum = typer.Option(
        ...,
        "--provider",
        "-p",
        help="Cloud provider (aws, azure, gcp)",
    ),
    max_age_hours: int = typer.Option(24, "--max-age-hours", help="Stale threshold in hours"),
    auto_sync: bool = typer.Option(False, "--auto-sync", help="Re-sync stale services immediately"),
    region: str = typer.Option(
        ...,
        "--regions",
        "-r",
        help="Comma-separated regions for stale re-sync",
    ),
):
    """
    List (or auto re-sync) services that haven't been synced recently.

    \b
    Example — show stale, then re-sync them:
      sync stale -a 123456789012 --max-age-hours 12 --auto-sync -r us-east-1
    """

    async def _run():
        app = get_app()
        stale = await app.repo.sync.get_stale_services(account_id, max_age_hours=max_age_hours)
        if provider:
            stale = [s for s in stale if s.get("provider") == provider]

        if not stale:
            console.print(f"[green]All services are fresh (within {max_age_hours}h)[/green]")
            return

        stale_keys = [s["service_key"] for s in stale]

        table = Table(title=f"Stale services — {account_id}")
        table.add_column("Service", style="yellow")
        table.add_column("Provider", style="dim", width=8)
        table.add_column("Last completed", style="dim")
        table.add_column("Status", style="dim")
        for s in stale:
            table.add_row(
                s.get("service_key", "?"),
                s.get("provider", "?"),
                s.get("last_completed_at", "never"),
                s.get("status", "?"),
            )
        console.print(table)

        if not auto_sync:
            return

        regions = normalize_region(provider, region)
        console.print(f"\n[cyan]Auto-syncing {len(stale_keys)} stale services...[/cyan]")
        pipeline = Pipeline(app.neo4j, app.redis)
        result = await pipeline.run(
            account_id=account_id,
            provider=provider,
            service_keys=stale_keys,
            regions=regions,
        )
        _print_result(result)

    run_async(_run)
