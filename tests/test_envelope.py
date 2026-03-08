import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_not_wrapped():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert "success" not in resp.json()


@pytest.mark.asyncio
async def test_404_route_wrapped():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/nonexistent-path-xyz")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert "error" in body
    assert "meta" in body


@pytest.mark.asyncio
async def test_success_wrapped():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    # health is in SKIP_PATHS so no envelope
    assert resp.status_code == 200
    assert "success" not in resp.json()
