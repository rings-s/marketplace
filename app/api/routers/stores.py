from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.repositories.store import StoreRepository
from app.core.exceptions import ForbiddenError, ConflictError
from app.core.cache import cache_get, cache_set, cache_delete

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=StoreResponse, status_code=201)
async def create_store(
    body: StoreCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = StoreRepository(session)
    existing = await repo.get_by_owner(current_user.id)
    if existing:
        raise ConflictError("Store already exists for this user")
    store = await repo.create(owner_user_id=current_user.id, **body.model_dump())
    return store


@router.get("/me", response_model=StoreResponse)
async def get_my_store(current_user: CurrentUser, session: AsyncSession = Depends(get_db)):
    repo = StoreRepository(session)
    from app.core.exceptions import NotFoundError
    store = await repo.get_by_owner(current_user.id)
    if not store:
        raise NotFoundError("You don't have a store")
    return store


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(store_id: UUID, session: AsyncSession = Depends(get_db)):
    cache_key = f"store:{store_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    repo = StoreRepository(session)
    store = await repo.get_or_404(store_id)

    from app.schemas.store import StoreResponse as StoreResp
    store_data = StoreResp.model_validate(store).model_dump()
    await cache_set(cache_key, store_data, ttl=120)
    return store


@router.patch("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: UUID,
    body: StoreUpdate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    repo = StoreRepository(session)
    store = await repo.get_or_404(store_id)
    if store.owner_user_id != current_user.id:
        raise ForbiddenError()
    updates = body.model_dump(exclude_none=True)
    if updates:
        await repo.update(store_id, **updates)
    await cache_delete(f"store:{store_id}")
    return await repo.get(store_id)
