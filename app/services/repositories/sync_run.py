from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.constants import Node
from app.models.graph import SyncRun
from app.services.neo4j import Neo4jService


class SyncRepository:
    def __init__(self, driver: Neo4jService):
        self.driver = driver

    # ── SyncRun (whole-run record, written once at completion) ────────────

    async def record_sync_run(self, sync_run: SyncRun) -> None:
        """
        Persist a completed SyncRun node and link it to the Account.
        Called ONCE per pipeline.run() at the end — never mid-run.
        """
        query = """
        CREATE (r:SyncRun)
        SET r = $props
        WITH r
        MATCH (a:Account {id: $account_id})
        MERGE (a)-[:HAS_SYNC]->(r)
        """
        await self.driver.execute_query(
            query,
            {"props": sync_run.to_dict(), "account_id": sync_run.account_id},
        )

    async def get_latest_sync(self, account_id: str) -> Optional[SyncRun]:
        query = """
        MATCH (a:Account {id: $account_id})-[:HAS_SYNC]->(r:SyncRun)
        RETURN r
        ORDER BY r.started_at DESC
        LIMIT 1
        """
        results = await self.driver.execute_query(query, {"account_id": account_id})
        return SyncRun(**results[0]["r"]) if results else None

    async def list_syncs(
        self,
        account_id: str,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> list[SyncRun]:
        query = """
        MATCH (a:Account {id: $account_id})-[:HAS_SYNC]->(r:SyncRun)
        WHERE ($status IS NULL OR r.status = $status)
        RETURN r
        ORDER BY r.started_at DESC
        LIMIT $limit
        """
        results = await self.driver.execute_query(
            query, {"account_id": account_id, "status": status, "limit": limit}
        )
        return [SyncRun(**r["r"]) for r in results]

    # ── ServiceSyncRecord (per-service last state, upserted at completion) ─

    async def upsert_service_record(
        self,
        account_id: str,
        provider: str,
        service_key: str,
        status: str,
        regions: list[str],
        update_tag: int,
        error: Optional[str] = None,
    ) -> None:
        """
        Upsert the permanent per-service sync record.
        One node per (account_id, service_key) — always reflects the latest run.
        """
        query = """
        MERGE (r:ServiceSyncRecord {
            account_id: $account_id,
            service_key: $service_key
        })
        SET r.provider          = $provider,
            r.last_status       = $status,
            r.last_completed_at = $completed_at,
            r.last_error        = $error,
            r.last_regions      = $regions,
            r.last_update_tag   = $update_tag
        WITH r
        MATCH (a:Account {id: $account_id})
        MERGE (a)-[:HAS_SERVICE_SYNC]->(r)
        """
        await self.driver.execute_query(
            query,
            {
                "account_id": account_id,
                "service_key": service_key,
                "provider": provider,
                "status": status,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error": error,
                "regions": regions,
                "update_tag": update_tag,
            },
        )

    async def get_service_statuses(self, account_id: str) -> list[dict]:
        """
        Read per-service last-sync records from Neo4j.
        Used by sync status — shows historical completed/failed state.
        """
        query = """
        MATCH (a:Account {id: $account_id})-[:HAS_SERVICE_SYNC]->(r:ServiceSyncRecord)
        RETURN r.service_key    AS service_key,
               r.provider       AS provider,
               r.last_status    AS status,
               r.last_completed_at AS last_completed_at,
               r.last_regions   AS regions,
               r.last_error     AS error
        ORDER BY r.service_key
        """
        results = await self.driver.execute_query(query, {"account_id": account_id})
        return [
            {
                "service_key": r["service_key"],
                "provider": r["provider"],
                "status": r["status"],
                "last_completed_at": r["last_completed_at"],
                "regions": r["regions"] or [],
                "error": r["error"],
            }
            for r in results
        ]

    async def get_stale_services(self, account_id: str, max_age_hours: int = 24) -> list[dict]:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=max_age_hours)).isoformat()
        query = """
        MATCH (a:Account {id: $account_id})-[:HAS_SERVICE_SYNC]->(r:ServiceSyncRecord)
        WHERE r.last_status = 'failed'
           OR (
               r.last_completed_at IS NOT NULL
               AND datetime(r.last_completed_at) < datetime($cutoff)
           )
        RETURN r.service_key    AS service_key,
               r.provider       AS provider,
               r.last_status    AS status,
               r.last_completed_at AS last_completed_at
        ORDER BY r.service_key
        """
        results = await self.driver.execute_query(
            query, {"account_id": account_id, "cutoff": cutoff}
        )
        return [
            {
                "service_key": r["service_key"],
                "provider": r["provider"],
                "status": r["status"],
                "last_completed_at": r["last_completed_at"],
            }
            for r in results
        ]
