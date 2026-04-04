from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ServiceDefinition:
    key: str
    provider: str  # "aws" | "azure" | "gcp"
    display_name: str
    module_path: str
    function_name: str
    requires_region: bool = True
    requires_account_id: bool = True
    depends_on: list[str] = field(default_factory=list)
    description: str = ""

    # ── GCP only ─────────────────────────────────────────────────────────
    # Service name passed to googleapiclient.discovery.build()
    # Also used as the kwarg name when calling the intel fn (e.g. "compute",
    # "storage", "dns") — Cartography names the param after the client.
    gcp_client_service: Optional[str] = None
    gcp_client_version: str = "v1"

    # Name of a function in gcp_prefetch.py that resolves the optional 3rd
    # positional argument some GCP intel fns require (zones, clusters, etc.)
    # fn signature: (client, project_id) -> value
    gcp_prefetch: Optional[str] = None

    # ── AWS / Azure static overrides ─────────────────────────────────────
    # Rarely needed — only for kwargs that can't be inferred from context.
    extra_kwargs: dict = field(default_factory=dict)
