import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.location import LocationService


def test_haversine_known_distance():
    svc = LocationService()
    # Riyadh to Jeddah approx ~850 km
    riyadh_lat, riyadh_lon = 24.7136, 46.6753
    jeddah_lat, jeddah_lon = 21.4858, 39.1925
    dist = svc.haversine_km(riyadh_lat, riyadh_lon, jeddah_lat, jeddah_lon)
    assert 820 < dist < 880, f"Expected ~850 km, got {dist:.1f}"


def test_haversine_zero_distance():
    svc = LocationService()
    dist = svc.haversine_km(24.7136, 46.6753, 24.7136, 46.6753)
    assert dist == pytest.approx(0.0, abs=1e-6)


def test_haversine_short_distance():
    svc = LocationService()
    # ~1 degree lat ≈ 111 km
    dist = svc.haversine_km(24.0, 46.0, 25.0, 46.0)
    assert 110 < dist < 112


@pytest.mark.asyncio
async def test_geocode_returns_coordinates():
    mock_response = MagicMock()
    mock_response.json.return_value = [{"lat": "24.6877", "lon": "46.7219"}]
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.location.httpx.AsyncClient", return_value=mock_client):
        svc = LocationService()
        result = await svc.geocode("الرياض")

    assert result is not None
    lat, lon = result
    assert lat == pytest.approx(24.6877)
    assert lon == pytest.approx(46.7219)


@pytest.mark.asyncio
async def test_geocode_returns_none_when_no_results():
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.location.httpx.AsyncClient", return_value=mock_client):
        svc = LocationService()
        result = await svc.geocode("xyznotacityatall12345")

    assert result is None


@pytest.mark.asyncio
async def test_reverse_geocode_returns_address():
    mock_response = MagicMock()
    mock_response.json.return_value = {"display_name": "الرياض، منطقة الرياض، المملكة العربية السعودية"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.location.httpx.AsyncClient", return_value=mock_client):
        svc = LocationService()
        address = await svc.reverse_geocode(24.7136, 46.6753)

    assert address is not None
    assert "الرياض" in address


@pytest.mark.asyncio
async def test_reverse_geocode_returns_none_on_error():
    mock_response = MagicMock()
    mock_response.json.return_value = {"error": "Unable to geocode"}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.location.httpx.AsyncClient", return_value=mock_client):
        svc = LocationService()
        address = await svc.reverse_geocode(0.0, 0.0)

    assert address is None
