from app.core import logging
from neo4j import AsyncGraphDatabase, Query
from app.core.config import settings
from app.core.exceptions import DatabaseError
from typing import Any, Dict, List, Optional

logger = logging.get_logger("neo4j")


class Neo4jService:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
        self.driver = None

    async def connect(self) -> None:
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            await self.driver.verify_connectivity()
            logger.info("Connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise DatabaseError("Failed to connect to Neo4j database", {"error": str(e)})

    async def close(self) -> None:
        if self.driver:
            await self.driver.close()
            logger.info("Disconnected from Neo4j")

    async def execute_query(
        self, query: str | Query, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.driver:
            raise DatabaseError("Neo4j driver not initialized")

        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run(query, parameters or {})  # type: ignore
                records = await result.fetch(-1)
                return [record.data() for record in records]
        except Exception as e:
            logger.error(f"Neo4j query error: {str(e)}")
            raise DatabaseError("Database query failed", {"error": str(e)})

    async def create_node(self, label: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = f"""
        CREATE (n:{label} $props)
        RETURN n
        """
        try:
            results = await self.execute_query(query, {"props": properties})
            return results[0]["n"] if results else None
        except Exception as e:
            logger.error(f"Failed to create node: {str(e)}")
            raise

    async def find_node(self, label: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        props_match = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"MATCH (n:{label} {{{props_match}}}) RETURN n"
        try:
            results = await self.execute_query(query, properties)
            return results[0]["n"] if results else None
        except Exception as e:
            logger.error(f"Failed to find node: {str(e)}")
            raise

    async def health_check(self) -> bool:
        try:
            if self.driver:
                await self.driver.verify_connectivity()
                return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {str(e)}")
        return False
