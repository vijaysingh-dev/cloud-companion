from typing import List
from app.services.neo4j import Neo4jService
from app.models.graph import Organization, APIKey, Account, SyncMetadata


class OrganizationRepository:
    def __init__(self, driver: Neo4jService):
        self.driver = driver

    # ---------------------------------------------------------------------------
    # Organization methods
    # ---------------------------------------------------------------------------

    async def create_org(self, org: Organization) -> Organization | None:
        query = """
        CREATE (o:Organization $props)
        RETURN o
        """
        results = await self.driver.execute_query(query, {"props": org.to_dict()})
        return Organization(**results[0]["o"]) if results else None

    async def get_org_by_name(self, name: str) -> Organization | None:
        query = """
        MATCH (o:Organization {name: $name})
        RETURN o
        """
        results = await self.driver.execute_query(query, {"name": name})
        return Organization(**results[0]["o"]) if results else None

    async def list_organizations(self) -> List[Organization]:
        query = """
        MATCH (o:Organization)
        RETURN o
        """
        results = await self.driver.execute_query(query)
        return [Organization(**r["o"]) for r in results]

    async def delete_org(self, org_id: str) -> None:
        query = """
        MATCH (o:Organization {org_id: $org_id})
        DETACH DELETE o
        """
        await self.driver.execute_query(query, {"org_id": org_id})

    # ---------------------------------------------------------------------------
    # APIKey methods
    # ---------------------------------------------------------------------------

    async def create_api_key(self, key: APIKey) -> APIKey | None:
        query = """
        MATCH (o:Organization {org_id: $org_id})
        CREATE (k:APIKey $props)
        CREATE (o)-[:HAS_API_KEY]->(k)
        RETURN k
        """
        results = await self.driver.execute_query(
            query, {"org_id": key.org_id, "props": key.to_dict()}
        )
        return APIKey(**results[0]["k"]) if results else None

    async def list_api_keys(self, org_id: str) -> List[APIKey]:
        query = """
        MATCH (o:Organization {org_id: $org_id})-[:HAS_API_KEY]->(k)
        RETURN k
        """
        results = await self.driver.execute_query(query, {"org_id": org_id})
        return [APIKey(**r["k"]) for r in results]

    async def revoke_api_key(self, key_id: str):
        query = """
        MATCH (k:APIKey {key_id: $key_id})
        SET k.is_active = false
        """
        await self.driver.execute_query(query, {"key_id": key_id})

    async def find_api_key_by_hash(self, hashed: str) -> APIKey | None:
        query = """
        MATCH (k:APIKey {hashed_key: $hash})
        RETURN k
        """
        results = await self.driver.execute_query(query, {"hash": hashed})
        return APIKey(**results[0]["k"]) if results else None

    # ---------------------------------------------------------------------------
    # Account methods
    # ---------------------------------------------------------------------------

    async def create_account(self, account: Account) -> Account | None:
        query = """
        MATCH (o:Organization {org_id: $org_id})
        CREATE (c:Account $props)
        CREATE (o)-[:OWNS]->(c)
        RETURN c
        """
        results = await self.driver.execute_query(
            query,
            {
                "org_id": account.org_id,
                "props": account.to_dict(),
            },
        )
        return Account(**results[0]["c"]) if results else None

    async def get_account(self, account_id: str) -> Account | None:
        query = """
        MATCH (c:Account {account_id: $account_id})
        RETURN c
        """
        results = await self.driver.execute_query(query, {"account_id": account_id})
        return Account(**results[0]["c"]) if results else None

    async def list_accounts(self, org_id: str) -> List[Account]:
        query = """
        MATCH (o:Organization {org_id: $org_id})-[:OWNS]->(c)
        RETURN c
        """
        results = await self.driver.execute_query(query, {"org_id": org_id})
        return [Account(**r["c"]) for r in results]

    # ---------------------------------------------------------------------------
    # Sync methods
    # ---------------------------------------------------------------------------

    async def create_sync_metadata(
        self,
        metadata: SyncMetadata,
    ) -> SyncMetadata | None:
        query = """
        MATCH (c:Account {account_id: $account_id})
        CREATE (s:SyncMetadata $props)
        CREATE (c)-[:HAS_SYNC]->(s)
        RETURN s
        """
        results = await self.driver.execute_query(
            query,
            {
                "account_id": metadata.account_id,
                "props": metadata.to_dict(),
            },
        )
        return SyncMetadata(**results[0]["s"]) if results else None

    async def complete_sync(self, sync_id: str) -> None:
        query = """
        MATCH (s:SyncMetadata {sync_id: $sync_id})
        SET s.completed_at = datetime()
        """
        await self.driver.execute_query(query, {"sync_id": sync_id})
