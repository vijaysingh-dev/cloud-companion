import uuid, logging
from typing import Optional, Dict, Any, List

from app.services.neo4j import Neo4jService
from app.services.weaviate import WeaviateService
from app.services.llm import LLMService
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        neo4j_service: Neo4jService,
        weaviate_service: WeaviateService,
        llm_service: LLMService,
    ):
        self.neo4j = neo4j_service
        self.weaviate = weaviate_service
        self.llm = llm_service

    async def create_conversation(self, org_id: str) -> str:
        try:
            conversation_id = str(uuid.uuid4())
            query = """
            CREATE (c:Conversation {id: $id, org_id: $org_id, created_at: datetime()})
            RETURN c.id
            """
            results = await self.neo4j.execute_query(
                query, {"id": conversation_id, "org_id": org_id}
            )
            return conversation_id
        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            raise DatabaseError("Failed to create conversation")

    async def add_message(
        self,
        conversation_id: str,
        org_id: str,
        role: str,
        content: str,
    ) -> str:
        try:
            message_id = str(uuid.uuid4())
            query = """
            MATCH (c:Conversation {id: $conv_id})
            CREATE (m:Message {id: $msg_id, role: $role, content: $content, created_at: datetime()})
            CREATE (c)-[:HAS_MESSAGE]->(m)
            RETURN m.id
            """
            results = await self.neo4j.execute_query(
                query,
                {
                    "conv_id": conversation_id,
                    "msg_id": message_id,
                    "role": role,
                    "content": content,
                },
            )
            return message_id
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")
            raise DatabaseError("Failed to add message")

    async def get_conversation_context(
        self, conversation_id: str, limit: int = 5
    ) -> List[Dict[str, str]]:
        try:
            query = """
            MATCH (c:Conversation {id: $conv_id})-[:HAS_MESSAGE]->(m:Message)
            RETURN m.role as role, m.content as content
            ORDER BY m.created_at DESC
            LIMIT $limit
            """
            results = await self.neo4j.execute_query(
                query, {"conv_id": conversation_id, "limit": limit}
            )
            return [{"role": r.get("role"), "content": r.get("content")} for r in reversed(results)]
        except Exception as e:
            logger.error(f"Failed to get conversation context: {str(e)}")
            return []

    async def search_resources(self, org_id: str, query: str) -> List[Dict[str, Any]]:
        try:
            embeddings = await self.llm.create_embeddings(query)
            results = await self.weaviate.search_vectors(
                collection="CloudResource", vector=embeddings, limit=5
            )
            return results
        except Exception as e:
            logger.error(f"Failed to search resources: {str(e)}")
            return []

    async def generate_response(
        self,
        conversation_id: str,
        org_id: str,
        user_message: str,
        context_resources: Optional[List[str]] = None,
    ) -> str:
        try:
            context_data = []
            if context_resources:
                query = """
                MATCH (r:CloudResource)
                WHERE r.id IN $ids
                RETURN r.name as name, r.metadata as metadata, r.resource_type as type
                """
                results = await self.neo4j.execute_query(query, {"ids": context_resources})
                context_data = results

            context_string = "\n".join(
                [
                    f"Resource: {r.get('name', 'N/A')}, Type: {r.get('type', 'N/A')}, Metadata: {r.get('metadata', {})}"
                    for r in context_data
                ]
            )

            messages = await self.get_conversation_context(conversation_id)
            messages.append({"role": "user", "content": user_message})

            response = await self.llm.generate_response(
                messages=messages, context=context_string if context_string else None
            )

            await self.add_message(conversation_id, org_id, "assistant", response)

            return response
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise
