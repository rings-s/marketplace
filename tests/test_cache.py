import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_cache_set_and_get():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"key": "value"}'

    with patch("app.core.cache._get_redis", return_value=mock_redis):
        from app.core.cache import cache_get
        result = await cache_get("test-key")
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_cache_miss_returns_none():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    with patch("app.core.cache._get_redis", return_value=mock_redis):
        from app.core.cache import cache_get
        result = await cache_get("missing-key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_delete():
    mock_redis = AsyncMock()

    with patch("app.core.cache._get_redis", return_value=mock_redis):
        from app.core.cache import cache_delete
        await cache_delete("some-key")
    mock_redis.delete.assert_called_once_with("some-key")
