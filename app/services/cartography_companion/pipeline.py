# app/services/cartography_companion/pipeline.py

"""
Shared sync pipeline — consumed by CLI and Celery tasks.

Changes vs. previous version
-----------------------------
1. `set_status("running")` is gone.  Status is written atomically inside
   `acquire_lock` (status=running) and `release_lock` (terminal state).
2. `release_lock` now receives the terminal status so lock release and status
   flip are a single logical operation with no gap.
3. `is_running` still checks the lock key (unchanged), but the status key is
   now always consistent with it.
"""


import logging
import time
from uuid import uuid4

from app.core.constants import CloudProviderEnum, utc_now
from app.models.graph import ServiceSyncRecord, SyncRun

from app.services.neo4j import Neo4jService
from app.services.redis import RedisService
from app.services.repositories.sync_run import SyncRepository

from .registry.service_registry import registry
from .sync.executor import execute_service_sync
from .sync.provider_context import (
    build_aws_context,
    build_azure_context,
    build_gcp_context,
)
from .redis_tracker import RedisSyncTracker
from .relationship_enricher import RelationshipEnricher

logger = logging.getLogger(__name__)


def patch_cartography_cleanup():
    # Replacing cleanup with soft delete in cartography
    from cartography.graph.job import GraphJob

    original = GraphJob.from_node_schema

    def patched(cls, node_schema, parameters, iterationsize=100, cascade_delete=False):
        job = original(node_schema, parameters, iterationsize, cascade_delete)

        for stmt in job.statements:
            query = stmt.query

            query = query.replace("DETACH DELETE n", "SET n.status = 'stale'")
            query = query.replace("DETACH DELETE child", "SET child.status = 'stale'")
            query = query.replace("DELETE n", "SET n.status = 'stale'")
            query = query.replace("DELETE r", "SET r.status = 'stale'")
            query = query.replace("DELETE s", "SET s.status = 'stale'")

            stmt.query = query

        return job

    setattr(GraphJob, "from_node_schema", classmethod(patched))


class SyncResult:
    def __init__(self):
        self.succeeded: list[str] = []
        self.failed: dict[str, str] = {}  # service_key -> error message (runtime OR invalid)
        self.skipped: dict[str, str] = {}  # service_key -> reason
        self.invalid: set[str] = set()  # subset of failed — never reached execution
        self.update_tag: int = 0

    @property
    def all_ok(self) -> bool:
        return not self.failed

    @property
    def runtime_failures(self) -> dict[str, str]:
        """Services that started but crashed — excludes validation failures."""
        return {k: v for k, v in self.failed.items() if k not in self.invalid}

    def summary(self) -> str:
        lines = [f"update_tag={self.update_tag}"]
        if self.succeeded:
            lines.append(f"  ok      : {', '.join(self.succeeded)}")
        if self.skipped:
            for k, reason in self.skipped.items():
                lines.append(f"  skipped : {k} ({reason})")
        if self.invalid:
            for k in self.invalid:
                lines.append(f"  invalid : {k} — {self.failed[k]}")
        if self.runtime_failures:
            for k, err in self.runtime_failures.items():
                lines.append(f"  FAILED  : {k} — {err}")
        return "\n".join(lines)


class Pipeline:
    """
    Shared sync pipeline used by both CLI and app/Celery tasks.

    - Calls cartography intel modules directly (no CLI, no cleanup)
    - Distributed lock per account+service via Redis
    - Per-service history in Neo4j (ServiceSyncRecord)
    - Whole-run summary node (SyncRun) written once at the end
    - Relationship enrichment runs after every successful batch
    """

    def __init__(self, neo4j: Neo4jService, redis: RedisService):
        self.neo4j = neo4j
        self.sync_repo = SyncRepository(neo4j)
        self.redis_tracker = RedisSyncTracker(redis)
        self.enricher = RelationshipEnricher(neo4j)

    # ── provider context ─────────────────────────────────────────────────────

    def _build_provider_context(
        self,
        provider: CloudProviderEnum,
        account_id: str,
        service_keys: list[str],
    ):
        if provider == CloudProviderEnum.AWS:
            return build_aws_context(service_keys)
        if provider == CloudProviderEnum.AZURE:
            return build_azure_context(account_id)
        if provider == CloudProviderEnum.GCP:
            return build_gcp_context(account_id)
        raise ValueError(f"Unsupported provider: {provider}")

    # ── main entry point ─────────────────────────────────────────────────────

    async def run(
        self,
        account_id: str,
        provider: CloudProviderEnum,
        service_keys: list[str],
        regions: list[str],
        force: bool = False,
    ) -> SyncResult:
        result = SyncResult()
        result.update_tag = int(time.time() * 1000)
        sync_run_id = str(uuid4())
        started_at = utc_now()

        # ── Resolve, validate, and topologically order ────────────────────
        ordered_services, expand_errors = registry.expand(service_keys, provider=provider.value)

        for key, reason in expand_errors.items():
            result.failed[key] = reason
            result.invalid.add(key)
            logger.warning(f"[{provider.value}] invalid service '{key}': {reason}")
            await self.redis_tracker.set_invalid(account_id, key, reason)

        if not ordered_services:
            logger.error("No valid services to sync after validation.")
            return result

        patch_cartography_cleanup()

        # ── Build provider context once for the whole run ─────────────────
        try:
            ctx = self._build_provider_context(
                provider, account_id, [s.key for s in ordered_services]
            )
        except Exception as e:
            for svc in ordered_services:
                result.failed[svc.key] = f"provider auth failed: {e}"
            logger.exception(f"Failed to build {provider.value} context: {e}")
            return result

        # ── Per-service loop ──────────────────────────────────────────────
        for svc in ordered_services:
            svc_region = regions if svc.requires_region else []

            # Lock check (reads lock key, not status key)
            if not force and await self.redis_tracker.is_running(account_id, svc.key):
                result.skipped[svc.key] = "already running"
                logger.info(f"  ~ [{svc.key}] skipped (already running)")
                continue

            # Acquire lock — also atomically sets status=running
            acquired = await self.redis_tracker.acquire_lock(account_id, svc.key, sync_run_id)
            if not acquired:
                result.skipped[svc.key] = "lock not acquired"
                continue

            terminal_status = "failed"
            terminal_extra: dict = {}

            try:
                logger.info(
                    f"  → [{svc.key}] syncing "
                    f"(regions={', '.join(svc_region) if svc_region else 'global'})"
                )
                await execute_service_sync(
                    svc=svc,
                    neo4j=self.neo4j,
                    ctx=ctx,
                    regions=svc_region,
                    update_tag=result.update_tag,
                    account_id=account_id,
                )

                await self.sync_repo.upsert_service_record(
                    ServiceSyncRecord(
                        account_id=account_id,
                        service_key=svc.key,
                        provider=provider,
                        last_status="completed",
                        last_update_tag=result.update_tag,
                        last_regions=svc_region,
                        last_completed_at=utc_now(),
                    )
                )
                result.succeeded.append(svc.key)
                terminal_status = "completed"
                logger.info(f"  ✓ [{svc.key}] done")

            except Exception as e:
                error_msg = str(e)
                logger.exception(f"  ✗ [{svc.key}] FAILED: {error_msg}")
                await self.sync_repo.upsert_service_record(
                    ServiceSyncRecord(
                        account_id=account_id,
                        service_key=svc.key,
                        provider=provider,
                        last_status="failed",
                        last_update_tag=result.update_tag,
                        last_regions=svc_region,
                        last_completed_at=utc_now(),
                        last_error=error_msg,
                    )
                )
                result.failed[svc.key] = error_msg
                terminal_extra = {"error": error_msg}

            finally:
                # Lock release + status flip are atomic in release_lock.
                # No window where lock is gone but status still says "running".
                await self.redis_tracker.release_lock(
                    account_id,
                    svc.key,
                    terminal_status=terminal_status,
                    extra=terminal_extra,
                )

        # ── Write whole-run SyncRun node once at the end ──────────────────
        overall_status = (
            "completed"
            if not result.runtime_failures
            else "failed" if not result.succeeded else "partial"
        )
        sync_run = SyncRun(
            id=sync_run_id,
            provider=provider,
            account_id=account_id,
            update_tag=result.update_tag,
            services=service_keys,
            regions=regions,
            trigger=None,
            status=overall_status,
            started_at=started_at,
            completed_at=utc_now(),
            succeeded=result.succeeded,
            failed=list(result.runtime_failures.keys()),
            skipped=list(result.skipped.keys()),
        )
        await self.sync_repo.record_sync_run(sync_run)

        if result.succeeded:
            logger.info("Running relationship enrichment...")
            await self.enricher.run_all(account_id=account_id)

        return result
