import pytest
from app.core.security import create_access_token, decode_token, create_refresh_token
from app.core.exceptions import UnauthorizedError


def test_access_token_roundtrip():
    token = create_access_token("user-123")
    payload = decode_token(token, "access")
    assert payload["sub"] == "user-123"


def test_refresh_token_roundtrip():
    token = create_refresh_token("user-123")
    payload = decode_token(token, "refresh")
    assert payload["sub"] == "user-123"


def test_wrong_token_type_raises():
    token = create_access_token("user-123")
    with pytest.raises(UnauthorizedError):
        decode_token(token, "refresh")
