import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.message import Conversation
from app.models.user import User
from app.schemas.message import ConversationResponse, MessageCreate, MessageResponse
from app.services.message import (
    get_messages,
    get_or_create_conversation,
    get_unread_count,
    get_user_conversations,
    send_message,
)
from app.utils.deps import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

active_connections: dict[str, list[WebSocket]] = {}


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversations = await get_user_conversations(user, db)
    result = []
    for conv in conversations:
        unread = await get_unread_count(user.id, conv.id)

        # get the other person's name
        other_id = conv.provider_id if user.id == conv.client_id else conv.client_id
        other_result = await db.execute(select(User).where(User.id == other_id))
        other_user = other_result.scalar_one_or_none()

        result.append({
            "id": conv.id,
            "client_id": conv.client_id,
            "provider_id": conv.provider_id,
            "request_id": conv.request_id,
            "unread_count": unread,
            "other_name": other_user.full_name if other_user else "Unknown",
        })
    return result


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def start_conversation(
    provider_id: uuid.UUID,
    request_id: uuid.UUID | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_or_create_conversation(user.id, provider_id, request_id, db)
    return {
        "id": conv.id,
        "client_id": conv.client_id,
        "provider_id": conv.provider_id,
        "request_id": conv.request_id,
        "unread_count": 0,
        "other_name": None,
    }


@router.get("/conversations/{conversation_id}", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    page: int = 1,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_messages(conversation_id, user, db, page)


@router.post("/conversations/{conversation_id}", response_model=MessageResponse, status_code=201)
async def post_message(
    conversation_id: uuid.UUID,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    message = await send_message(conversation_id, data.content, user, db)

    conv_key = str(conversation_id)
    if conv_key in active_connections:
        for ws in active_connections[conv_key]:
            await ws.send_json({
                "id": str(message.id),
                "sender_id": str(message.sender_id),
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            })

    return message


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    conversation_id: str,
    websocket: WebSocket,
):
    await websocket.accept()
    if conversation_id not in active_connections:
        active_connections[conversation_id] = []
    active_connections[conversation_id].append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[conversation_id].remove(websocket)
        if not active_connections[conversation_id]:
            del active_connections[conversation_id]