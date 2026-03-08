from decimal import Decimal
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, CursorItemListResponse, NearbyItemResponse
from app.services.location import LocationService
from app.repositories.item import ItemRepository
from app.core.enums import ItemCondition, ItemStatus, SellerType, UserRole
from app.core.exceptions import ForbiddenError
from app.core.cache import cache_get, cache_set, cache_delete

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=CursorItemListResponse)
async def list_items(
    cursor: str | None = None,
    city: str | None = None,
    category: str | None = None,
    condition: ItemCondition | None = None,
    seller_type: SellerType | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    repo = ItemRepository(session)
    # Cursor-based pagination (primary)
    items, next_cursor, has_more = await repo.list_with_cursor(
        cursor=cursor,
        size=size,
        city=city,
        category=category,
        condition=condition,
        seller_type=seller_type,
        min_price=min_price,
        max_price=max_price,
        q=q,
    )
    _, total = await repo.list_with_filters(
        city=city,
        category=category,
        condition=condition,
        seller_type=seller_type,
        min_price=min_price,
        max_price=max_price,
        q=q,
        offset=0,
        limit=1,
    )
    return CursorItemListResponse(items=items, next_cursor=next_cursor, has_more=has_more, total=total)


@router.get("/nearby", response_model=list[NearbyItemResponse])
async def list_nearby_items(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, ge=0.1, le=100.0),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    repo = ItemRepository(session)
    candidates = await repo.list_near(lat=lat, lon=lon, radius_km=radius_km, size=size)
    location_svc = LocationService()
    results: list[NearbyItemResponse] = []
    for item in candidates:
        dist = location_svc.haversine_km(lat, lon, item.lat, item.lon)  # type: ignore[arg-type]
        if dist <= radius_km:
            results.append(
                NearbyItemResponse(
                    **ItemResponse.model_validate(item).model_dump(), distance_km=round(dist, 3)
                )
            )
        if len(results) >= size:
            break
    results.sort(key=lambda r: r.distance_km)
    return results


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID, session: AsyncSession = Depends(get_db)):
    cache_key = f"item:{item_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    repo = ItemRepository(session)
    item = await repo.get_or_404(item_id)
    await repo.increment_views(item_id)

    item_data = ItemResponse.model_validate(item).model_dump()
    await cache_set(cache_key, item_data, ttl=60)
    return item


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    body: ItemCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    if current_user.role == UserRole.buyer:
        raise ForbiddenError("Buyers cannot create listings")

    repo = ItemRepository(session)
    data = body.model_dump(exclude={"tag_ids"})

    if body.seller_type == SellerType.individual:
        data["individual_seller_id"] = current_user.id
    else:
        data["store_id"] = None  # caller should ensure store exists

    item = await repo.create(**data)
    if body.tag_ids:
        await repo.set_tags(item.id, body.tag_ids)
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    body: ItemUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = ItemRepository(session)
    item = await repo.get_or_404(item_id)

    is_owner = (item.individual_seller_id == current_user.id)
    if not is_owner and current_user.role != UserRole.admin:
        raise ForbiddenError()

    updates = body.model_dump(exclude_none=True, exclude={"tag_ids"})
    updates["updated_at"] = datetime.now(timezone.utc)
    if updates:
        await repo.update(item_id, **updates)

    if body.tag_ids is not None:
        await repo.set_tags(item_id, body.tag_ids)

    await cache_delete(f"item:{item_id}")
    return await repo.get(item_id)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = ItemRepository(session)
    item = await repo.get_or_404(item_id)

    is_owner = (item.individual_seller_id == current_user.id)
    if not is_owner and current_user.role != UserRole.admin:
        raise ForbiddenError()

    await repo.update(item_id, status=ItemStatus.deleted)
    await cache_delete(f"item:{item_id}")
