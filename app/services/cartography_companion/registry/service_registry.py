import json
from difflib import get_close_matches
from pathlib import Path
from typing import Optional

from .service_definition import ServiceDefinition
from .aws_services import AWS_SERVICES
from .azure_services import AZURE_SERVICES
from .gcp_services import GCP_SERVICES

_RESOURCE_FILE = Path(__file__).resolve().parent / "resources.json"


def _load_resource_keys() -> dict[str, set[str]]:
    try:
        payload = json.loads(_RESOURCE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"aws": set(), "azure": set(), "gcp": set()}
    return {provider: set(payload.get(provider, [])) for provider in ("aws", "azure", "gcp")}


def _unknown_reason(key: str, available: list[str], as_dep_of: Optional[str] = None) -> str:
    """
    Build a human-readable error string for an unresolvable service key.
    Includes a fuzzy suggestion if one exists.
    """
    suggestion = get_close_matches(key, available, n=1, cutoff=0.5)
    hint = f" Did you mean '{suggestion[0]}'?" if suggestion else ""

    if as_dep_of:
        return f"required by '{as_dep_of}' as a dependency but not registered.{hint}"
    return f"unknown service.{hint}"


class ServiceRegistry:
    """
    Single source of truth for all syncable services across providers.
    Both CLI and app import this — never duplicate service definitions.
    """

    def __init__(self):
        self._services: dict[str, dict[str, ServiceDefinition]] = {
            "aws": {},
            "azure": {},
            "gcp": {},
        }
        allowed_keys = _load_resource_keys()

        for svc in AWS_SERVICES:
            if svc.key in allowed_keys.get("aws", set()):
                self._services["aws"][svc.key] = svc

        for svc in AZURE_SERVICES:
            if svc.key in allowed_keys.get("azure", set()):
                self._services["azure"][svc.key] = svc

        for svc in GCP_SERVICES:
            if svc.key in allowed_keys.get("gcp", set()):
                self._services["gcp"][svc.key] = svc

    # ── Lookup ────────────────────────────────────────────────────────────

    def get(self, key: str, provider: str) -> Optional[ServiceDefinition]:
        return self._services.get(provider, {}).get(key)

    def list_all(self, provider: str) -> list[ServiceDefinition]:
        return list(self._services.get(provider, {}).values())

    def available_keys(self, provider: str) -> list[str]:
        return sorted(self._services.get(provider, {}).keys())

    # ── Expand ────────────────────────────────────────────────────────────

    def expand(
        self,
        keys: list[str],
        provider: str,
    ) -> tuple[list[ServiceDefinition], dict[str, str]]:
        """
        Resolves requested keys into a dependency-ordered list of ServiceDefinitions.

        Returns:
            (ordered, errors)
            - ordered: valid services with deps first, no duplicates
            - errors:  {service_key: reason} for anything that couldn't be resolved

        Invalid keys (requested or pulled in as deps) are collected into errors
        with fuzzy suggestions where possible. The topo sort only runs over the
        clean set — no logic is repeated across phases.
        """
        errors: dict[str, str] = {}
        available = self.available_keys(provider)

        # ── Phase 1: single-pass dep graph walk ───────────────────────────
        # Traverse the full graph (requested keys + transitive deps) in one
        # pass. Each key is visited once; unknown keys go straight to errors
        # with context about whether the user requested them or a dep pulled
        # them in. No separate validation loop needed.

        clean: dict[str, ServiceDefinition] = {}  # key → resolved definition
        # Track which parent pulled in each dep so the error message is useful
        pulled_by: dict[str, str] = {}  # dep_key → requesting_key

        queue: list[str] = list(keys)  # start with user-requested keys
        requested: set[str] = set(keys)  # for error context
        visited: set[str] = set()

        while queue:
            key = queue.pop(0)
            if key in visited:
                continue
            visited.add(key)

            svc = self.get(key, provider)
            if svc is None:
                parent = pulled_by.get(key)  # None if user requested it
                errors[key] = _unknown_reason(
                    key,
                    available,
                    as_dep_of=parent if key not in requested else None,
                )
                continue

            clean[key] = svc

            # Enqueue deps, recording who pulled them in
            for dep in svc.depends_on:
                if dep not in visited:
                    pulled_by.setdefault(dep, key)
                    queue.append(dep)

        if not clean:
            return [], errors

        # ── Phase 2: Kahn's topo sort over clean keys only ────────────────
        all_keys = set(clean.keys())

        in_degree: dict[str, int] = {k: 0 for k in all_keys}
        dependents: dict[str, list[str]] = {k: [] for k in all_keys}

        for key in all_keys:
            for dep in clean[key].depends_on:
                if dep in all_keys:  # skip errored deps
                    in_degree[key] += 1
                    dependents[dep].append(key)

        ready = [k for k, deg in in_degree.items() if deg == 0]
        ordered: list[ServiceDefinition] = []

        while ready:
            key = ready.pop(0)
            ordered.append(clean[key])
            for dependent in dependents[key]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    ready.append(dependent)

        if len(ordered) != len(all_keys):
            synced = {svc.key for svc in ordered}
            for key in all_keys - synced:
                errors[key] = "circular dependency detected — could not resolve order"

        return ordered, errors


registry = ServiceRegistry()
