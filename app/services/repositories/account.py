from typing import Optional, List

from app.core.constants import Node
from app.services.neo4j import Neo4jService

from app.models.graph import Account


class AccountRepository:
    def __init__(self, driver: Neo4jService):
        self.driver = driver

    async def create_account(self, account: Account) -> Optional[Account]:
        props = account.to_dict()
        # ON MATCH only updates mutable fields — account_id and provider never change
        result = await self.driver.merge_node(
            label=Node.ACCOUNT,
            merge_key="id",
            merge_value=props["id"],
            on_create_props=props,
            on_match_props={
                "name": props["name"],
            },
        )
        if not result:
            return None
        await self.driver.create_relationship(
            from_label=Node.ORGANIZATION,
            from_id=account.org_id,
            rel_type="OWNS",
            to_label=Node.ACCOUNT,
            to_id=props["id"],
        )
        return Account(**result)

    async def get_account(self, account_id: str) -> Optional[Account]:
        result = await self.driver.find_node(Node.ACCOUNT, account_id)
        return Account(**result) if result else None

    async def list_accounts(self, org_id: str) -> List[Account]:
        results = await self.driver.list_nodes(Node.ACCOUNT, filters={"org_id": org_id})
        return [Account(**r) for r in results]

    async def update_account_last_synced(self, account_id: str) -> None:
        from app.core.constants import utc_now

        await self.driver.update_node(
            Node.ACCOUNT, account_id, {"last_synced": utc_now().isoformat()}
        )
