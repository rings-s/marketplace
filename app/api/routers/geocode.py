import httpx
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.services.location import LocationService

router = APIRouter(prefix="/geocode", tags=["geocode"])


class GeocodeSearchRequest(BaseModel):
    q: str


class GeocodeSearchResponse(BaseModel):
    lat: float
    lon: float


class ReverseGeocodeResponse(BaseModel):
    lat: float
    lon: float
    address: str


@router.get("/reverse", response_model=ReverseGeocodeResponse)
async def reverse_geocode(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    svc = LocationService()
    try:
        address = await svc.reverse_geocode(lat, lon)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Geocoding upstream error: {exc.response.status_code}")
    if address is None:
        raise HTTPException(status_code=404, detail="No address found for the given coordinates")
    return ReverseGeocodeResponse(lat=lat, lon=lon, address=address)


@router.post("/search", response_model=GeocodeSearchResponse)
async def search_geocode(body: GeocodeSearchRequest):
    svc = LocationService()
    try:
        result = await svc.geocode(body.q)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Geocoding upstream error: {exc.response.status_code}")
    if result is None:
        raise HTTPException(status_code=404, detail="No location found for the given query")
    lat, lon = result
    return GeocodeSearchResponse(lat=lat, lon=lon)
