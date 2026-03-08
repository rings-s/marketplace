from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.chat import ThreadCreate, MessageCreate, ThreadResponse, MessageResponse
from app.repositories.chat import ChatRepository
from app.core.exceptions import ForbiddenError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/threads", response_model=list[ThreadResponse])
async def list_threads(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(session)
    return await repo.get_threads_for_user(current_user.id)


@router.post("/threads", response_model=ThreadResponse, status_code=201)
async def create_thread(
    body: ThreadCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(session)
    # Reuse existing thread if present
    existing = await repo.get_thread_by_participants(
        buyer_id=current_user.id,
        seller_id=body.seller_id,
        item_id=body.item_id,
    )
    if existing:
        return existing

    thread = await repo.create(
        item_id=body.item_id,
        buyer_id=current_user.id,
        seller_id=body.seller_id,
    )

    if body.initial_message:
        await repo.create_message(
            thread_id=thread.id,
            sender_id=current_user.id,
            content_text=body.initial_message,
            sent_at=datetime.now(timezone.utc),
        )

    return thread


@router.get("/threads/{thread_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    thread_id: UUID,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(session)
    thread = await repo.get_or_404(thread_id)
    if current_user.id not in (thread.buyer_id, thread.seller_id):
        raise ForbiddenError()
    offset = (page - 1) * size
    return await repo.get_messages_by_thread(thread_id, offset=offset, limit=size)


@router.post("/threads/{thread_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    thread_id: UUID,
    body: MessageCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(session)
    thread = await repo.get_or_404(thread_id)
    if current_user.id not in (thread.buyer_id, thread.seller_id):
        raise ForbiddenError()

    return await repo.create_message(
        thread_id=thread_id,
        sender_id=current_user.id,
        content_text=body.content_text,
        content_type=body.content_type.value,
        media_url=body.media_url,
        sent_at=datetime.now(timezone.utc),
    )
