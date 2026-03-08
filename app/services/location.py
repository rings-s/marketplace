import math
import structlog
import httpx

logger = structlog.get_logger()
NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
NOMINATIM_HEADERS = {
    "User-Agent": "KSAFurnitureMarketplace/1.0 (contact@marketplace.sa)",
    "Accept-Language": "ar,en",
}


class LocationService:
    async def geocode(self, address: str) -> tuple[float, float] | None:
        params = {"q": address, "format": "jsonv2", "limit": 1, "countrycodes": "sa"}
        async with httpx.AsyncClient(headers=NOMINATIM_HEADERS, timeout=10) as client:
            resp = await client.get(f"{NOMINATIM_BASE}/search", params=params)
            resp.raise_for_status()
            results = resp.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])

    async def reverse_geocode(self, lat: float, lon: float) -> str | None:
        params = {"lat": lat, "lon": lon, "format": "jsonv2"}
        async with httpx.AsyncClient(headers=NOMINATIM_HEADERS, timeout=10) as client:
            resp = await client.get(f"{NOMINATIM_BASE}/reverse", params=params)
            resp.raise_for_status()
            data = resp.json()
        if "error" in data:
            return None
        return data.get("display_name")

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6_371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.asin(math.sqrt(a))
