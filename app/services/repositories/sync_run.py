# app/services/repositories/sync_run.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.constants import Node, Relationship
from app.models.graph import ServiceSyncRecord, SyncRun
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
        props = sync_run.to_dict()
        await self.driver.create_node(Node.SYNC_RUN, props)
        await self.driver.create_relationship(
            Node.ACCOUNT,
            sync_run.account_id,
            Relationship.HAS_SYNC,
            Node.SYNC_RUN,
            props["id"],
        )

    async def get_latest_sync(self, account_id: str) -> Optional[SyncRun]:
        query = f"""
        MATCH (a:{Node.ACCOUNT} {{id: $account_id}})-[:{Relationship.HAS_SYNC}]->(r:{Node.SYNC_RUN})
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
        query = f"""
        MATCH (a:{Node.ACCOUNT} {{id: $account_id}})-[:{Relationship.HAS_SYNC}]->(r:{Node.SYNC_RUN})
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
    async def upsert_service_record(self, record: ServiceSyncRecord) -> None:
        """
        Upsert the permanent per-service sync record.
        One node per (account_id, service_key) — always reflects the latest run.
        """
        props = record.to_dict()
        await self.driver.merge_node(
            Node.SERVICE_SYNC_RECORD,
            "id",
            props["id"],
            on_create_props=props,
            on_match_props=props,
        )
        await self.driver.create_relationship(
            Node.ACCOUNT,
            record.account_id,
            Relationship.HAS_SERVICE_SYNC,
            Node.SERVICE_SYNC_RECORD,
            props["id"],
        )

    async def get_service_statuses(self, account_id: str) -> list[dict]:
        """
        Read per-service last-sync records from Neo4j.
        Used by sync status — shows historical completed/failed state.
        """
        query = f"""
        MATCH (a:{Node.ACCOUNT} {{id: $account_id}})-[:{Relationship.HAS_SERVICE_SYNC}]->(r:{Node.SERVICE_SYNC_RECORD})
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
        query = f"""
        MATCH (a:{Node.ACCOUNT} {{id: $account_id}})-[:{Relationship.HAS_SERVICE_SYNC}]->(r:{Node.SERVICE_SYNC_RECORD})
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
