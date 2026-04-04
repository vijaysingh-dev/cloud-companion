from typing import List, Optional

from app.core.constants import Node
from app.services.neo4j import Neo4jService
from app.models.graph import Organization


class OrganizationRepository:
    def __init__(self, driver: Neo4jService):
        self.driver = driver

    async def create_org(self, org: Organization) -> Optional[Organization]:
        result = await self.driver.create_node(Node.ORGANIZATION, org.to_dict())
        return Organization(**result) if result else None

    async def get_org(self, org_id: str) -> Optional[Organization]:
        result = await self.driver.find_node(Node.ORGANIZATION, org_id)
        return Organization(**result) if result else None

    async def get_org_by_name(self, name: str) -> Optional[Organization]:
        results = await self.driver.list_nodes(Node.ORGANIZATION, filters={"name": name}, limit=1)
        return Organization(**results[0]) if results else None

    async def list_organizations(self) -> List[Organization]:
        results = await self.driver.list_nodes(Node.ORGANIZATION, filters={"is_active": True})
        return [Organization(**r) for r in results]

    async def delete_org(self, org_id: str) -> None:
        await self.driver.update_node(Node.ORGANIZATION, org_id, {"is_active": False})
