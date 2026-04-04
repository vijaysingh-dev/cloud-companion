import logging
from typing import Optional

from app.models.graph import SyncRun
from app.core.application import Application


logger = logging.getLogger("cartography-companion")


class SyncLifecycleManager:
    """
    Wraps a cartography sync run. Call pre_sync() before, post_sync() after.
    Never modifies cartography's own write logic.
    """

    def __init__(self, app: Application, stale_threshold_syncs: int = 3):
        self.app = app
        self.stale_threshold = stale_threshold_syncs

    async def pre_sync(
        self, account_id: str, services: list[str], regions: list[str], trigger: str
    ) -> SyncRun:
        sync = SyncRun(account_id=account_id, services=services, regions=regions, trigger=trigger)

        await self.app.repo.sync.create_sync_run(sync)

        logger.info(f"SyncRun {sync.sync_id} started for account {account_id}")
        return sync

    async def post_sync(
        self, sync: SyncRun, sync_timestamp: int, error: Optional[Exception] = None
    ):
        """
        Called after cartography finishes. sync_timestamp is the lastupdated
        value cartography used (epoch ms int).
        """

        status = "failed" if error else "completed"
        await self.app.repo.sync.complete_sync(sync_id=sync.sync_id, status=status)

        # Link all nodes touched in this sync to this SyncMetadata node
        # Cartography stamps lastupdated on everything it touches — we use that
        await self.app.neo4j.execute_query(
            query="""
            MATCH (n)
            WHERE n.lastupdated = $sync_timestamp
              AND NOT n:SyncMetadata
            MATCH (s:SyncMetadata {id: $sync_id})
            MERGE (n)-[:HAS_SYNC]->(s)
            """,
            params={"sync_timestamp": sync_timestamp, "sync_id": sync.sync_id},
        )

        if not error:
            await self._mark_stale_nodes(sync.account_id, sync_timestamp)

        logger.info(f"SyncRun {sync.sync_id} {sync.status}")

    async def _mark_stale_nodes(self, account_id: str, current_sync_ts: int):
        """
        Nodes that haven't been seen in `stale_threshold` consecutive syncs
        get status=stale. We NEVER delete — the LLM needs to know they existed.
        """
        # Find the Nth-most-recent sync timestamp for this account
        result = await self.app.neo4j.execute_query(
            query="""
            MATCH (s:SyncMetadata {account_id: $account_id, status: 'completed'})
            WITH s ORDER BY s.sync_timestamp DESC
            SKIP $threshold LIMIT 1
            RETURN s.sync_timestamp AS cutoff_ts
            """,
            params={"account_id": account_id, "threshold": self.stale_threshold},
        )

        if not result:
            return  # Not enough syncs yet to mark anything stale

        cutoff_ts = result[0]["cutoff_ts"]
        # Mark nodes not seen since the cutoff as stale
        await self.app.neo4j.execute_query(  # type: ignore
            query="""
            MATCH (n)
            WHERE n.lastupdated < $cutoff_ts
              AND n.account_id = $account_id
              AND NOT n:SyncMetadata
              AND NOT n:Organization
            SET n.status = 'stale',
                n.stale_since = $current_ts
            """,
            params={
                "cutoff_ts": cutoff_ts,
                "account_id": account_id,
                "current_ts": current_sync_ts,
            },
        )

        logger.info(f"Marked stale nodes for account {account_id} (cutoff: {cutoff_ts})")
