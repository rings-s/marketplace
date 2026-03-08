import pytest
from app.core.pagination import encode_cursor, decode_cursor
from datetime import datetime, timezone
from uuid import uuid4


def test_cursor_roundtrip():
    now = datetime.now(timezone.utc)
    uid = uuid4()
    cursor = encode_cursor(now, uid)
    t, i = decode_cursor(cursor)
    assert i == uid
    assert abs((t - now).total_seconds()) < 1


def test_invalid_cursor_raises():
    with pytest.raises(ValueError):
        decode_cursor("not-valid-base64!!")
