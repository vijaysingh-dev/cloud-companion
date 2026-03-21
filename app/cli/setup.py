import json
import asyncio
from typing import List, Annotated

import typer
from app.cli.runtime import run_async, get_app

from app.core.constants import CloudProviderEnum
from app.core.config import settings


cli = typer.Typer()


@cli.command()
async def setup(
    provider: Annotated[CloudProviderEnum, typer.Argument(help="Cloud provider (aws, azure, gcp)")],
    regions: str = typer.Option(settings.AWS_REGIONS, help="Comma separated regions (AWS only)"),
):

    args = build_cartography_args(provider, ",".join(regions))
    await run_cartography_sync(*args)

    # await app.repo.organization.complete_sync(sync.id)
    print("[green]Initial sync completed[/green]")


def get_default_services(provider) -> List[str]:
    with open(settings.ROOT_DIR / "app/core/resources.json", "r") as f:
        default_services = json.load(f)
    return default_services.get(provider, [])


def build_cartography_args(provider, regions):
    services = ",".join(get_default_services(provider))
    if provider == "aws":
        aws_args = ["--aws-sync-all-profiles"] if settings.AWS_PROFILE_MODE == "MULTI" else []
        aws_args.extend(["--aws-regions", regions, "--aws-requested-syncs", services])
        return aws_args
    elif provider == "azure":
        azure_args = []
        if settings.AZURE_SP_AUTH:
            azure_args.extend(
                [
                    "--azure-sp-auth",
                    "--azure-tenant-id",
                    settings.AZURE_TENANT_ID,
                    "--azure-client-id",
                    settings.AZURE_CLIENT_ID,
                    "--azure-client-secret-env-var",
                    settings.AZURE_CLIENT_SECRET,
                ]
            )
        if settings.AZURE_SUBSCRIPTION_ID:
            azure_args.extend(["--azure-subscription-id", settings.AZURE_SUBSCRIPTION_ID])
        else:
            azure_args.append("--azure-sync-all-subscriptions")
        return azure_args
    elif provider == "gcp":
        return ["--gcp-requested-syncs", services]
    return []


async def run_cartography_sync(*args):
    cmd = [
        "cartography",
        "--neo4j-uri",
        settings.NEO4J_URI,
        "--neo4j-user",
        settings.NEO4J_USER,
        "--neo4j-password",
        settings.NEO4J_PASSWORD,
        "--selected-modules",
        "aws,azure,gcp",
        *args,
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(stderr.decode())

    return stdout.decode()
