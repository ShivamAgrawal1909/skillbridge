import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Conversation, Message
from app.models.user import User


async def get_or_create_conversation(
    client_id: uuid.UUID,
    provider_id: uuid.UUID,
    request_id: uuid.UUID | None,
    db: AsyncSession,
) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.client_id == client_id,
            Conversation.provider_id == provider_id,
            Conversation.request_id == request_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            id=uuid.uuid4(),
            client_id=client_id,
            provider_id=provider_id,
            request_id=request_id,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    return conversation


async def get_user_conversations(user: User, db: AsyncSession) -> list[Conversation]:
    from app.models.user import UserRole

    if user.role == UserRole.client:
        condition = Conversation.client_id == user.id
    else:
        condition = Conversation.provider_id == user.id

    result = await db.execute(
        select(Conversation)
        .where(condition)
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()


async def send_message(
    conversation_id: uuid.UUID,
    content: str,
    sender: User,
    db: AsyncSession,
) -> Message:
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if sender.id not in (conversation.client_id, conversation.provider_id):
        raise HTTPException(status_code=403, detail="Not part of this conversation")

    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        sender_id=sender.id,
        content=content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    # increment unread count — only if Redis available
    from app.utils.redis import redis as redis_client
    if redis_client:
        other_id = conversation.provider_id if sender.id == conversation.client_id else conversation.client_id
        await redis_client.incr(f"unread:{other_id}:{conversation_id}")

    return message


async def get_messages(
    conversation_id: uuid.UUID,
    user: User,
    db: AsyncSession,
    page: int = 1,
    limit: int = 50,
) -> list[Message]:
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if user.id not in (conversation.client_id, conversation.provider_id):
        raise HTTPException(status_code=403, detail="Not part of this conversation")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    messages = result.scalars().all()

    # clear unread count — only if Redis available
    from app.utils.redis import redis as redis_client
    if redis_client:
        await redis_client.delete(f"unread:{user.id}:{conversation_id}")

    return messages


async def get_unread_count(user_id: uuid.UUID, conversation_id: uuid.UUID) -> int:
    from app.utils.redis import redis as redis_client
    if not redis_client:
        return 0
    count = await redis_client.get(f"unread:{user_id}:{conversation_id}")
    return int(count) if count else 0