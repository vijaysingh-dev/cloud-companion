import logging
from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect
from app.api.deps import RequestContext, get_request_context
from app.models.schema import ChatMessageRequest, ChatResponse
from app.services.neo4j import Neo4jService
from app.services.weaviate import WeaviateService
from app.services.llm import LLMService
from app.services.chat import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

neo4j_service = Neo4jService()
weaviate_service = WeaviateService()
llm_service = LLMService()
chat_service = ChatService(neo4j_service, weaviate_service, llm_service)


@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_conversation(
    context: RequestContext = Depends(get_request_context),
):
    try:
        conversation_id = await chat_service.create_conversation(context.org_id)
        return {"conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"Failed to start conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start conversation")


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessageRequest,
    context: RequestContext = Depends(get_request_context),
):
    try:
        if not message.conversation_id:
            message.conversation_id = await chat_service.create_conversation(context.org_id)

        await chat_service.add_message(
            message.conversation_id,
            context.org_id,
            "user",
            message.content,
        )

        response_text = await chat_service.generate_response(
            message.conversation_id,
            context.org_id,
            message.content,
            message.context_resources,
        )

        return ChatResponse(
            message_id="auto",
            conversation_id=message.conversation_id,
            content=response_text,
            confidence=0.95,
        )

    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")

            response = f"Echo: {data}"
            await websocket.send_text(response)

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")
