from typing import Any, Optional
from neo4j import Session
from dataclasses import dataclass, field


@dataclass
class ResourceContext:
    """Structured context passed to the LLM for a given resource."""
    node_id: str
    labels: list[str]
    properties: dict[str, Any]
    canonical_type: Optional[str]
    provider: Optional[str]
    status: str  # active | stale | unknown

    # Relationships: list of {rel_type, direction, neighbor_id, neighbor_labels, neighbor_props}
    relationships: list[dict[str, Any]] = field(default_factory=list)

    # Missing expected relationships (holes in the graph)
    missing_relationships: list[str] = field(default_factory=list)

    # Sync context
    last_synced: Optional[str] = None
    sync_age_hours: Optional[float] = None

    def to_llm_prompt_fragment(self) -> str:
        """
        Returns a compact natural-language summary.
        The main LLM uses this as context, not raw Cypher results.
        """
        lines = [
            f"Resource: {self.node_id}",
            f"Type: {self.canonical_type or self.labels[0]} ({self.provider or 'unknown provider'})",
            f"Status: {self.status}",
        ]
        if self.last_synced:
            lines.append(f"Last seen: {self.last_synced} ({self.sync_age_hours:.1f}h ago)")

        if self.properties:
            # Include only non-internal props
            display_props = {
                k: v for k, v in self.properties.items()
                if not k.startswith("_") and k not in ("lastupdated", "source")
                and v is not None
            }
            if display_props:
                lines.append(f"Properties: {display_props}")

        if self.relationships:
            lines.append("Relationships:")
            for rel in self.relationships:
                direction = "→" if rel["direction"] == "outgoing" else "←"
                lines.append(
                    f"  {direction} [{rel['rel_type']}] "
                    f"{rel['neighbor_labels'][0]}({rel['neighbor_id']})"
                )

        if self.missing_relationships:
            lines.append(
                f"NOTE: Expected relationships not found in graph: "
                f"{', '.join(self.missing_relationships)} — data may be incomplete."
            )

        return "\n".join(lines)


# Expected relationships per canonical type — used to detect gaps
EXPECTED_RELATIONSHIPS: dict[str, list[str]] = {
    "Compute": ["PROTECTS", "DEPLOYED_IN", "ASSUMES_IDENTITY", "MONITORED_BY"],
    "ServerlessFunction": ["PROTECTS", "ASSUMES_IDENTITY", "TRIGGERS", "EMITS_LOGS_TO"],
    "Database": ["PROTECTS", "DEPLOYED_IN", "ENCRYPTED_BY"],
    "LoadBalancer": ["HOSTS", "DEPLOYED_IN", "PROTECTS"],
    "API": ["TRIGGERS", "EXPOSES"],
}


class GraphContextBuilder:

    def __init__(self, session: Session, max_hops: int = 2):
        self.session = session
        self.max_hops = max_hops

    def build_for_resource(self, resource_id: str) -> Optional[ResourceContext]:
        """
        Primary method. Given any resource id (cartography 'id' field),
        returns full context including neighborhood and gap detection.
        """
        node_data = self._fetch_node(resource_id)
        if not node_data:
            return None

        props = dict(node_data["n"])
        labels = list(node_data["labels"])
        canonical_type = props.get("canonical_type")
        status = props.get("status", "active")

        relationships = self._fetch_neighborhood(resource_id)
        missing = self._detect_missing_relationships(canonical_type, relationships)
        sync_info = self._fetch_sync_info(resource_id)

        return ResourceContext(
            node_id=resource_id,
            labels=labels,
            properties=props,
            canonical_type=canonical_type,
            provider=props.get("provider"),
            status=status,
            relationships=relationships,
            missing_relationships=missing,
            last_synced=sync_info.get("completed_at"),
            sync_age_hours=sync_info.get("age_hours"),
        )

    def build_for_query(
        self,
        canonical_type: str,
        account_id: str,
        region: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> list[ResourceContext]:
        """
        For user queries like 'show all databases' or 'EC2 instances in us-east-1'.
        Returns a list of contexts, one per matching resource.
        """
        where_clauses = [f"n:{canonical_type}", f"n.account_id = $account_id"]
        params: dict[str, Any] = {"account_id": account_id}

        if region:
            where_clauses.append("n.region = $region")
            params["region"] = region
        if filters:
            for k, v in filters.items():
                where_clauses.append(f"n.{k} = ${k}")
                params[k] = v

        where_str = " AND ".join(where_clauses)
        result = self.session.run(f"""
            MATCH (n)
            WHERE {where_str}
            RETURN n.id AS node_id
            LIMIT 50
        """, **params)

        return [
            ctx for row in result
            if (ctx := self.build_for_resource(row["node_id"])) is not None
        ]

    def _fetch_node(self, resource_id: str) -> Optional[dict]:
        result = self.session.run("""
            MATCH (n {id: $id})
            RETURN n, labels(n) AS labels
            LIMIT 1
        """, id=resource_id)
        return result.single()

    def _fetch_neighborhood(self, resource_id: str) -> list[dict]:
        result = self.session.run("""
            MATCH (n {id: $id})-[r]-(neighbor)
            RETURN
                type(r)         AS rel_type,
                CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END AS direction,
                neighbor.id     AS neighbor_id,
                neighbor.name   AS neighbor_name,
                labels(neighbor) AS neighbor_labels,
                properties(neighbor) AS neighbor_props
            LIMIT 50
        """, id=resource_id)

        return [dict(row) for row in result]

    def _detect_missing_relationships(
        self,
        canonical_type: Optional[str],
        found_relationships: list[dict],
    ) -> list[str]:
        if not canonical_type:
            return []
        expected = EXPECTED_RELATIONSHIPS.get(canonical_type, [])
        found_rel_types = {r["rel_type"] for r in found_relationships}
        return [r for r in expected if r not in found_rel_types]

    def _fetch_sync_info(self, resource_id: str) -> dict:
        result = self.session.run("""
            MATCH (n {id: $id})-[:HAS_SYNC]->(s:SyncMetadata)
            WITH s ORDER BY s.sync_timestamp DESC LIMIT 1
            RETURN s.completed_at AS completed_at,
                   duration.between(
                       datetime(s.completed_at),
                       datetime()
                   ).hours AS age_hours
        """, id=resource_id)
        record = result.single()
        return dict(record) if record else {}