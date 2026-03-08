import json
import pytest
from unittest.mock import AsyncMock
from app.services.otp import OTPService


@pytest.mark.asyncio
async def test_send_generates_otp():
    svc = OTPService()
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = False
    svc._redis = mock_redis
    ttl = await svc.send("user-123")
    assert ttl == 300
    mock_redis.setex.assert_called()


@pytest.mark.asyncio
async def test_send_rate_limited():
    svc = OTPService()
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = True
    svc._redis = mock_redis
    with pytest.raises(ValueError, match="already sent"):
        await svc.send("user-123")


@pytest.mark.asyncio
async def test_verify_correct_code():
    svc = OTPService()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"code": "123456", "attempts": 0})
    svc._redis = mock_redis
    result = await svc.verify("user-123", "123456")
    assert result is True
    mock_redis.delete.assert_called_once()


@pytest.mark.asyncio
async def test_verify_wrong_code():
    svc = OTPService()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"code": "123456", "attempts": 0})
    svc._redis = mock_redis
    result = await svc.verify("user-123", "999999")
    assert result is False


@pytest.mark.asyncio
async def test_verify_max_attempts():
    svc = OTPService()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"code": "123456", "attempts": 2})
    svc._redis = mock_redis
    with pytest.raises(ValueError, match="Too many"):
        await svc.verify("user-123", "999999")
