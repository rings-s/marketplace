import json
from typing import Any
import redis.asyncio as aioredis
from app.config import settings


async def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def cache_get(key: str) -> Any | None:
    r = await _get_redis()
    raw = await r.get(key)
    if raw:
        return json.loads(raw)
    return None


async def cache_set(key: str, value: Any, ttl: int) -> None:
    r = await _get_redis()
    await r.setex(key, ttl, json.dumps(value, default=str))


async def cache_delete(key: str) -> None:
    r = await _get_redis()
    await r.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    r = await _get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)
