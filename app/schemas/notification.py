from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Any
from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    type: NotificationType
    title_ar: str
    title_en: str
    body_ar: str
    body_en: str
    data: dict[str, Any]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CursorNotificationList(BaseModel):
    items: list[NotificationResponse]
    next_cursor: str | None
    has_more: bool
