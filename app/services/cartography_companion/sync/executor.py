import importlib
import inspect
import logging
import asyncio
from functools import partial
from typing import Any, Union

from ..registry.service_definition import ServiceDefinition
from .provider_context import AWSContext, AzureContext, GCPContext
from .gcp_prefetch import run_prefetch

logger = logging.getLogger(__name__)

ProviderContext = Union[AWSContext, AzureContext, GCPContext]

# Fixed GCP param names that are never the "client slot" or "prefetch slot"
_GCP_FIXED_PARAMS = frozenset(
    {"neo4j_session", "project_id", "gcp_update_tag", "update_tag", "common_job_parameters"}
)


# ── AWS ───────────────────────────────────────────────────────────────────────


def _build_aws_kwargs(
    svc: ServiceDefinition,
    session: Any,
    ctx: AWSContext,
    regions: list[str],
    account_id: str,
    update_tag: int,
) -> dict:
    kwargs: dict[str, Any] = {
        "neo4j_session": session,
        "boto3_session": ctx.boto_session,
        "regions": regions,
        "current_aws_account_id": account_id,
        "update_tag": update_tag,
        "common_job_parameters": {
            "UPDATE_TAG": update_tag,
            "AWS_ID": account_id,
        },
    }
    return kwargs


# ── Azure ─────────────────────────────────────────────────────────────────────


def _build_azure_kwargs(
    svc: ServiceDefinition,
    session: Any,
    ctx: AzureContext,
    account_id: str,
    update_tag: int,
) -> dict:
    module = importlib.import_module(svc.module_path)
    fn = getattr(module, svc.function_name)
    sig = inspect.signature(fn).parameters

    kwargs: dict[str, Any] = {
        "neo4j_session": session,
        "credentials": ctx.credentials,
        "subscription_id": account_id,
        "common_job_parameters": {
            "UPDATE_TAG": update_tag,
            "AZURE_SUBSCRIPTION_ID": account_id,
        },
    }
    # Azure modules use either update_tag or sync_tag — pass both, fn ignores unknown
    if "update_tag" in sig:
        kwargs["update_tag"] = update_tag
    if "sync_tag" in sig:
        kwargs["sync_tag"] = update_tag
    return kwargs


# ── GCP ───────────────────────────────────────────────────────────────────────


def _build_gcp_client(svc: ServiceDefinition, ctx: GCPContext) -> Any:
    from googleapiclient.discovery import build as gapi_build

    if not svc.gcp_client_service:
        raise ValueError(
            f"GCP service '{svc.key}' has no gcp_client_service set on its ServiceDefinition."
        )
    return gapi_build(
        svc.gcp_client_service,
        svc.gcp_client_version,
        credentials=ctx.google_credentials,
    )


def _build_gcp_kwargs(
    svc: ServiceDefinition,
    session: Any,
    ctx: GCPContext,
    update_tag: int,
) -> dict:
    client = _build_gcp_client(svc, ctx)

    # Inspect the intel fn to discover parameter names in order
    module = importlib.import_module(svc.module_path)
    fn = getattr(module, svc.function_name)
    param_names = list(inspect.signature(fn).parameters.keys())

    # Start with the fixed set every GCP fn receives
    kwargs: dict[str, Any] = {
        "neo4j_session": session,
        "project_id": ctx.project_id,
        "gcp_update_tag": update_tag,  # Cartography GCP uses gcp_update_tag, not update_tag
        "common_job_parameters": {
            "UPDATE_TAG": update_tag,
            "GCP_PROJECT_ID": ctx.project_id,
        },
    }

    # Slot 1 (after neo4j_session): the Resource client.
    # Cartography names this param after the service: "compute", "storage", "dns", etc.
    # We use gcp_client_service as the kwarg name — it matches Cartography's convention.
    client_param = svc.gcp_client_service  # e.g. "compute", "storage", "dns"
    if client_param and client_param in param_names:
        kwargs[client_param] = client
    elif len(param_names) > 1:
        # Fallback: use position [1] if name doesn't match — handles edge cases
        positional_client_name = param_names[1]
        if positional_client_name not in _GCP_FIXED_PARAMS:
            kwargs[positional_client_name] = client
            logger.debug(
                f"{svc.key}: client param name '{positional_client_name}' "
                f"doesn't match gcp_client_service='{client_param}', used positional fallback"
            )

    # Optional 3rd arg: zones, clusters, instances, etc.
    # Identify by finding the first non-fixed param that isn't the client slot
    if svc.gcp_prefetch:
        prefetch_value = run_prefetch(svc.gcp_prefetch, client, ctx.project_id)
        # Find its param name from the signature
        for name in param_names:
            if name not in _GCP_FIXED_PARAMS and name != client_param:
                kwargs[name] = prefetch_value
                break

    return kwargs


# ── Unified dispatcher ────────────────────────────────────────────────────────


def _build_kwargs(
    svc: ServiceDefinition,
    session: Any,
    ctx: ProviderContext,
    regions: list[str],
    account_id: str,
    update_tag: int,
) -> dict:
    if isinstance(ctx, AWSContext):
        kwargs = _build_aws_kwargs(svc, session, ctx, regions, account_id, update_tag)
    elif isinstance(ctx, AzureContext):
        kwargs = _build_azure_kwargs(svc, session, ctx, account_id, update_tag)
    elif isinstance(ctx, GCPContext):
        kwargs = _build_gcp_kwargs(svc, session, ctx, update_tag)
    else:
        raise ValueError(f"Unknown provider context: {type(ctx)}")

    # Static overrides always applied last — allows per-service tweaks
    if svc.extra_kwargs:
        kwargs.update(svc.extra_kwargs)

    return kwargs


def _call_intel_fn_blocking(
    svc: ServiceDefinition,
    neo4j_driver: Any,
    ctx: ProviderContext,
    regions: list[str],
    account_id: str,
    update_tag: int,
) -> None:
    module = importlib.import_module(svc.module_path)
    fn = getattr(module, svc.function_name)

    loop = None
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        with neo4j_driver.session() as session:
            kwargs = _build_kwargs(svc, session, ctx, regions, account_id, update_tag)
            logger.debug(
                f"[{svc.provider}] {svc.module_path}.{svc.function_name} "
                f"params={list(kwargs.keys())}"
            )
            fn(**kwargs)
    finally:
        if loop is not None and not loop.is_closed():
            loop.close()
            try:
                asyncio.set_event_loop(None)
            except RuntimeError:
                pass


async def execute_service_sync(
    svc: ServiceDefinition,
    neo4j: Any,
    ctx: ProviderContext,
    regions: list[str],
    update_tag: int,
    account_id: str,
) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        partial(
            _call_intel_fn_blocking,
            svc,
            neo4j.sync_driver,
            ctx,
            regions,
            account_id,
            update_tag,
        ),
    )
