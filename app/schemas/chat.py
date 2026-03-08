from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.core.enums import ContentType


class ThreadCreate(BaseModel):
    item_id: UUID
    seller_id: UUID
    initial_message: str | None = None


class MessageCreate(BaseModel):
    content_text: str | None = None
    content_type: ContentType = ContentType.text
    media_url: str | None = None


class MessageResponse(BaseModel):
    id: UUID
    thread_id: UUID
    sender_id: UUID
    content_text: str | None
    content_type: ContentType
    media_url: str | None
    is_read: bool
    sent_at: datetime
    delivered_at: datetime | None

    model_config = {"from_attributes": True}


class ThreadResponse(BaseModel):
    id: UUID
    item_id: UUID | None
    buyer_id: UUID
    seller_id: UUID
    last_message_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
