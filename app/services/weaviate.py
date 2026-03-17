import logging
from typing import Any, Dict, List, Optional

from app.core.exceptions import DatabaseError
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeaviateService:
    def __init__(self):
        self.host = settings.WEAVIATE_HOST
        self.client = None

    async def connect(self) -> None:
        try:
            import weaviate

            self.client = weaviate.connect_to_local(host=self.host)
            logger.info("Connected to Weaviate")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {str(e)}")
            raise DatabaseError("Failed to connect to Weaviate", {"error": str(e)})

    async def close(self) -> None:
        if self.client:
            self.client.close()
            logger.info("Disconnected from Weaviate")

    async def add_vector(
        self,
        collection: str,
        properties: Dict[str, Any],
        vector: List[float],
    ) -> Optional[str]:
        if not self.client:
            raise DatabaseError("Weaviate client not initialized")

        try:
            uuid = self.client.data_object.create(
                data_object=properties,
                class_name=collection,
                vector=vector,
            )
            return uuid
        except Exception as e:
            logger.error(f"Failed to add vector: {str(e)}")
            raise DatabaseError("Failed to add vector to Weaviate", {"error": str(e)})

    async def search_vectors(
        self,
        collection: str,
        vector: List[float],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise DatabaseError("Weaviate client not initialized")

        try:
            results = (
                self.client.query.get(collection)
                .with_near_vector({"vector": vector})
                .with_limit(limit)
                .do()
            )
            return results.get("data", {}).get("Get", {}).get(collection, [])
        except Exception as e:
            logger.error(f"Failed to search vectors: {str(e)}")
            raise DatabaseError("Failed to search vectors in Weaviate", {"error": str(e)})

    async def health_check(self) -> bool:
        try:
            if self.client:
                return self.client.is_ready()
        except Exception as e:
            logger.error(f"Weaviate health check failed: {str(e)}")
        return False
