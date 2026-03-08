import base64
import json
from datetime import datetime
from uuid import UUID


def encode_cursor(created_at: datetime, id: UUID) -> str:
    """Encode a stable cursor from created_at + id."""
    payload = {"t": created_at.isoformat(), "id": str(id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    """Decode cursor back to created_at + id."""
    try:
        payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
        return datetime.fromisoformat(payload["t"]), UUID(payload["id"])
    except Exception:
        raise ValueError("Invalid cursor")
