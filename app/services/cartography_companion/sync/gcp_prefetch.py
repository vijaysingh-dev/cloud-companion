"""
Resolvers for the optional 3rd positional argument in GCP intel sync functions.

Convention: fn(client, project_id) -> value_to_inject
Add a new function here + reference it by name in ServiceDefinition.gcp_prefetch.
"""

from typing import Any, Callable


def fetch_compute_zones(client: Any, project_id: str) -> list[dict]:
    """
    Used by: cartography.intel.gcp.compute.sync()  (param name: zones)
    """
    try:
        result = client.zones().list(project=project_id).execute()
        return result.get("items", [])
    except Exception:
        return []


def fetch_gke_clusters(client: Any, project_id: str) -> list[dict]:
    """
    Used by: cartography.intel.gcp.gke.sync()  (param name: clusters)
    """
    try:
        result = (
            client.projects()
            .locations()
            .clusters()
            .list(parent=f"projects/{project_id}/locations/-")
            .execute()
        )
        return result.get("clusters", [])
    except Exception:
        return []


def fetch_bigtable_instances(client: Any, project_id: str) -> list[dict]:
    """
    Used by: cartography.intel.gcp.bigtable.sync()  (param name: instances)
    """
    try:
        result = client.projects().instances().list(parent=f"projects/{project_id}").execute()
        return result.get("instances", [])
    except Exception:
        return []


# ── Registry ──────────────────────────────────────────────────────────────────

PREFETCH_REGISTRY: dict[str, Callable] = {
    "fetch_compute_zones": fetch_compute_zones,
    "fetch_gke_clusters": fetch_gke_clusters,
    "fetch_bigtable_instances": fetch_bigtable_instances,
}


def run_prefetch(name: str, client: Any, project_id: str) -> Any:
    fn = PREFETCH_REGISTRY.get(name)
    if fn is None:
        raise ValueError(
            f"Unknown gcp_prefetch '{name}'. "
            f"Register it in gcp_prefetch.py. Available: {list(PREFETCH_REGISTRY)}"
        )
    return fn(client, project_id)
