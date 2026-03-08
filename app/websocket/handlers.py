from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError
from app.repositories.user import UserRepository
from app.repositories.chat import ChatRepository
from app.websocket.manager import manager

ws_router = APIRouter()


async def _get_ws_user(token: str, session: AsyncSession):
    try:
        payload = decode_token(token, "access")
    except UnauthorizedError:
        return None
    repo = UserRepository(session)
    return await repo.get(payload["sub"])


@ws_router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
    session: AsyncSession = Depends(get_db),
):
    user = await _get_ws_user(token, session)
    if not user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    user_id = str(user.id)
    await manager.connect(ws, user_id)
    chat_repo = ChatRepository(session)

    try:
        while True:
            data = await ws.receive_json()
            event_type = data.get("type")

            if event_type == "message":
                thread_id = data.get("thread_id")
                content = data.get("content", "")
                msg = await chat_repo.create_message(
                    thread_id=thread_id,
                    sender_id=user_id,
                    content_text=content,
                    content_type="text",
                    sent_at=datetime.now(timezone.utc),
                )
                thread = await chat_repo.get_thread(thread_id)
                if thread:
                    receiver_id = (
                        str(thread.seller_id)
                        if str(thread.buyer_id) == user_id
                        else str(thread.buyer_id)
                    )
                    event = {
                        "type": "message",
                        "data": {
                            "id": str(msg.id),
                            "content": content,
                            "sender_id": user_id,
                            "thread_id": thread_id,
                            "sent_at": msg.sent_at.isoformat(),
                        },
                    }
                    await manager.broadcast_to_user(receiver_id, event)
                    await manager.broadcast_to_user(user_id, event)  # echo back

            elif event_type == "typing":
                thread_id = data.get("thread_id")
                thread = await chat_repo.get_thread(thread_id)
                if thread:
                    receiver_id = (
                        str(thread.seller_id)
                        if str(thread.buyer_id) == user_id
                        else str(thread.buyer_id)
                    )
                    await manager.broadcast_to_user(
                        receiver_id,
                        {"type": "typing", "data": {"thread_id": thread_id, "user_id": user_id}},
                    )

            elif event_type == "read":
                thread_id = data.get("thread_id")
                if thread_id:
                    await chat_repo.mark_messages_read(thread_id, user_id)

    except WebSocketDisconnect:
        await manager.disconnect(ws, user_id)
