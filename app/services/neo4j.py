# app/services/neo4j.py

import logging
from typing import Any, Optional

from neo4j import Query, Driver, GraphDatabase
from neo4j import AsyncDriver, AsyncGraphDatabase

from app.core.exceptions import DatabaseError
from app.core.config import settings


logger = logging.getLogger("neo4j")


class Neo4jService:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
        self._async_driver: Optional[AsyncDriver] = None
        self._sync_driver: Optional[Driver] = None

    @property
    def async_driver(self) -> AsyncDriver:
        if self._async_driver is None:
            raise RuntimeError("Neo4j not initialized. Call connect() first.")
        return self._async_driver

    @property
    def sync_driver(self) -> Driver:
        if self._sync_driver is None:
            raise RuntimeError("Neo4j not initialized. Call connect() first.")
        return self._sync_driver

    async def connect(self) -> None:
        try:
            self._async_driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            await self._async_driver.verify_connectivity()
            # Sync driver for cartography — same credentials, separate connection pool
            self._sync_driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._sync_driver.verify_connectivity()
            logger.info("Connected to Neo4j (async + sync)")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise DatabaseError("Failed to connect to Neo4j", {"error": str(e)})

    async def close(self) -> None:
        if self._async_driver:
            await self._async_driver.close()
        if self._sync_driver:
            self._sync_driver.close()
        logger.info("Disconnected from Neo4j")

    async def health_check(self) -> bool:
        try:
            if self._async_driver:
                await self._async_driver.verify_connectivity()
                return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
        return False

    async def execute_query(
        self, query: str | Query, params: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        if not self._async_driver:
            raise DatabaseError("Neo4j driver not initialized")
        try:
            async with self._async_driver.session(database=self.database) as session:
                result = await session.run(query, params or {})  # type: ignore
                return await result.data()
        except Exception as e:
            logger.error(f"Neo4j query error: {str(e)}")
            raise DatabaseError("Database query failed", {"error": str(e)})

    async def create_node(self, label: str, props: dict[str, Any]) -> Optional[dict[str, Any]]:
        query = f"""
        CREATE (n:{label})
        SET n = $props
        RETURN n
        """
        try:
            result = await self.execute_query(query, {"props": props})
            return result[0]["n"] if result else None
        except Exception as e:
            logger.error(f"Failed to create node [{label}]: {e}")
            raise

    async def merge_node(
        self,
        label: str,
        merge_key: str,
        merge_value: Any,
        on_create_props: dict[str, Any],
        on_match_props: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """
        MERGE on a single identity key. Properties split into:
        - on_create_props: written only when node is new
        - on_match_props:  written when node already exists (defaults to on_create_props)

        Use for: Account, EC2Instance, any resource that persists across syncs.
        """
        on_match_props = on_match_props or on_create_props

        query = f"""
        MERGE (n:{label} {{{merge_key}: $merge_value}})
        ON CREATE SET n = $on_create_props
        ON MATCH SET n += $on_match_props
        RETURN n
        """
        try:
            result = await self.execute_query(
                query,
                {
                    "merge_value": merge_value,
                    "on_create_props": on_create_props,
                    "on_match_props": on_match_props,
                },
            )
            return result[0]["n"] if result else None
        except Exception as e:
            logger.error(f"Failed to merge node [{label}] on {merge_key}={merge_value}: {e}")
            raise

    async def find_node(self, label: str, node_id: str) -> Optional[dict[str, Any]]:
        """
        Find a single node by its identity field.
        """
        query = f"""
        MATCH (n:{label} {{id: $node_id}})
        RETURN n
        """
        try:
            result = await self.execute_query(query, {"node_id": node_id})
            return result[0]["n"] if result else None
        except Exception as e:
            logger.error(f"Failed to find node [{label}] id={node_id}: {e}")
            raise

    async def list_nodes(
        self,
        label: str,
        filters: Optional[dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        """
        list nodes by label with optional exact-match filters.

        Filter keys are validated against an allowlist of safe characters
        to prevent Cypher injection via dict keys.
        """
        params: dict[str, Any] = {"limit": limit, "skip": skip}
        where_clause = ""

        if filters:
            _validate_property_keys(filters.keys())
            conditions = " AND ".join(f"n.{k} = $filter_{k}" for k in filters)
            where_clause = f"WHERE {conditions}"
            # prefix filter keys to avoid collision with other params
            params.update({f"filter_{k}": v for k, v in filters.items()})

        query = f"""
        MATCH (n:{label})
        {where_clause}
        RETURN n
        SKIP $skip
        LIMIT $limit
        """
        try:
            result = await self.execute_query(query, params)
            return [r["n"] for r in result]
        except Exception as e:
            logger.error(f"Failed to list nodes [{label}]: {e}")
            raise

    async def update_node(
        self,
        label: str,
        node_id: str,
        props: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """
        Partial update (+=) — only sets the given properties,
        does not remove existing ones.
        """
        query = f"""
        MATCH (n:{label} {{id: $node_id}})
        SET n += $props
        RETURN n
        """
        try:
            result = await self.execute_query(query, {"node_id": node_id, "props": props})
            return result[0]["n"] if result else None
        except Exception as e:
            logger.error(f"Failed to update node [{label}] id={node_id}: {e}")
            raise

    # -------------------------------------------------------------------------
    # Relationship operations
    # -------------------------------------------------------------------------

    async def create_relationship(
        self,
        from_label: str,
        from_id: Any,
        rel_type: str,
        to_label: str,
        to_id: Any,
        properties: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        MERGE the relationship — never creates duplicates even if called
        multiple times. Returns True if the relationship exists after the call.
        """
        properties = properties or {}
        set_clause = "SET r += $props" if properties else ""

        query = f"""
        MATCH (a:{from_label} {{id: $from_id}})
        MATCH (b:{to_label} {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        {set_clause}
        RETURN r
        """
        try:
            result = await self.execute_query(
                query, {"from_id": from_id, "to_id": to_id, "props": properties}
            )
            return bool(result)
        except Exception as e:
            logger.error(
                f"Failed to create relationship " f"[{from_label}]-[{rel_type}]->[{to_label}]: {e}"
            )
            raise

    async def delete_relationship(
        self,
        from_label: str,
        from_id: Any,
        rel_type: str,
        to_label: str,
        to_id: Any,
    ) -> None:
        """
        Hard delete a specific relationship (not the nodes).
        Relationships don't carry history the way nodes do,
        so hard delete is acceptable here.
        """
        query = f"""
        MATCH (a:{from_label} {{id: $from_id}})
              -[r:{rel_type}]->
              (b:{to_label} {{id: $to_id}})
        DELETE r
        """
        try:
            await self.execute_query(query, {"from_id": from_id, "to_id": to_id})
        except Exception as e:
            logger.error(
                f"Failed to delete relationship " f"[{from_label}]-[{rel_type}]->[{to_label}]: {e}"
            )
            raise


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

_SAFE_KEY_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "0123456789_")


def _validate_property_keys(keys) -> None:
    """
    Prevents Cypher injection through dict keys interpolated into f-strings.
    Only alphanumeric + underscore allowed — matches valid Neo4j property names.
    """
    for key in keys:
        if not all(c in _SAFE_KEY_CHARS for c in key):
            raise ValueError(
                f"Unsafe property key '{key}' — only alphanumeric and underscore allowed"
            )
