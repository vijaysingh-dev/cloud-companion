from typing import Optional, List

from app.core.constants import Node
from app.services.neo4j import Neo4jService

from app.models.graph import APIKey


class APIKeyRepository:
    def __init__(self, driver: Neo4jService):
        self.driver = driver

    async def create_api_key(self, key: APIKey) -> Optional[APIKey]:
        # Two-step: create the node, then link it — can't use create_node for
        # the relationship in one call, so raw query is correct here
        result = await self.driver.create_node(Node.API_KEY, key.to_dict())
        if not result:
            return None
        await self.driver.create_relationship(
            from_label=Node.ORGANIZATION,
            from_id=key.org_id,
            rel_type="HAS_API_KEY",
            to_label=Node.API_KEY,
            to_id=result["id"],
        )
        return APIKey(**result)

    async def list_api_keys(self, org_id: str) -> List[APIKey]:
        results = await self.driver.list_nodes(Node.API_KEY, filters={"org_id": org_id})
        return [APIKey(**r) for r in results]

    async def get_active_api_keys(self, org_id: str) -> List[APIKey]:
        # Needs expires_at comparison — list_nodes only does equality filters,
        # so raw query is the right call here
        from app.core.constants import utc_now

        query = """
        MATCH (o:Organization {id: $org_id})-[:HAS_API_KEY]->(k:APIKey)
        WHERE k.is_active = true AND k.expires_at > $now
        RETURN k
        """
        results = await self.driver.execute_query(
            query, {"org_id": org_id, "now": utc_now().isoformat()}
        )
        return [APIKey(**r["k"]) for r in results]

    async def revoke_api_key(self, key_id: str) -> None:
        await self.driver.update_node(Node.API_KEY, key_id, {"is_active": False})

    async def find_api_key_by_hash(self, hashed: str) -> Optional[APIKey]:
        # hashed_key is not the id field — can't use find_node,
        # but list_nodes with filters is safe here
        results = await self.driver.list_nodes(
            Node.API_KEY,
            filters={"hashed_key": hashed, "is_active": True},
            limit=1,
        )
        return APIKey(**results[0]) if results else None
