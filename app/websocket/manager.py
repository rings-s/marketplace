import asyncio
import json
from typing import Any
import redis.asyncio as aioredis
from fastapi import WebSocket
from app.config import settings


class ConnectionManager:
    """Redis pub/sub backed WebSocket manager for horizontal scaling."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}  # user_id -> [ws]
        self._redis: aioredis.Redis | None = None

    async def get_redis(self) -> aioredis.Redis:
        if not self._redis:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    def _channel(self, user_id: str) -> str:
        return f"chat:user:{user_id}"

    async def connect(self, ws: WebSocket, user_id: str) -> None:
        await ws.accept()
        self._connections.setdefault(user_id, []).append(ws)
        r = await self.get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(self._channel(user_id))
        asyncio.create_task(self._listen(pubsub, user_id))

    async def disconnect(self, ws: WebSocket, user_id: str) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)

    async def broadcast_to_user(self, user_id: str, event: dict[str, Any]) -> None:
        """Publish to Redis channel — works across multiple server instances."""
        r = await self.get_redis()
        await r.publish(self._channel(user_id), json.dumps(event))

    async def _listen(self, pubsub: aioredis.client.PubSub, user_id: str) -> None:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                except (json.JSONDecodeError, TypeError):
                    continue
                for ws in list(self._connections.get(user_id, [])):
                    try:
                        await ws.send_json(data)
                    except Exception:
                        pass


manager = ConnectionManager()
