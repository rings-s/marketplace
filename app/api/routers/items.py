from decimal import Decimal
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, CursorItemListResponse
from app.repositories.item import ItemRepository
from app.core.enums import ItemCondition, ItemStatus, SellerType, UserRole
from app.core.exceptions import ForbiddenError

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


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID, session: AsyncSession = Depends(get_db)):
    repo = ItemRepository(session)
    item = await repo.get_or_404(item_id)
    await repo.increment_views(item_id)
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
