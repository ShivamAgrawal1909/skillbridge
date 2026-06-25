import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    provider_id: uuid.UUID
    request_id: uuid.UUID | None
    unread_count: int = 0
    other_name: str | None = None

    model_config = {"from_attributes": True}