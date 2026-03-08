from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import CurrentUser
from app.schemas.review import ReviewCreate, ReviewResponse
from app.repositories.review import ReviewRepository
from app.repositories.order import OrderRepository
from app.repositories.store import StoreRepository
from app.core.enums import OrderStatus
from app.core.exceptions import ForbiddenError, ConflictError

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    body: ReviewCreate,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepository(session)
    order = await order_repo.get_or_404(body.order_id)

    if order.buyer_id != current_user.id:
        raise ForbiddenError("Only the buyer can leave a review")
    if order.status != OrderStatus.completed:
        raise ConflictError("Order must be completed before reviewing")

    review_repo = ReviewRepository(session)
    existing = await review_repo.get_by_order(body.order_id)
    if existing:
        raise ConflictError("Review already submitted for this order")

    review = await review_repo.create(
        order_id=body.order_id,
        reviewer_id=current_user.id,
        reviewee_id=order.seller_id,
        rating=body.rating,
        comment=body.comment,
    )

    # Update store avg_rating if seller has a store
    store_repo = StoreRepository(session)
    store = await store_repo.get_by_owner(order.seller_id)
    if store:
        avg = await review_repo.avg_rating(order.seller_id)
        await store_repo.update(store.id, avg_rating=Decimal(str(round(avg, 2))))

    return review


@router.get("/users/{user_id}", response_model=list[ReviewResponse])
async def get_user_reviews(
    user_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
):
    repo = ReviewRepository(session)
    reviews, _ = await repo.list_for_reviewee(user_id, offset=(page - 1) * size, limit=size)
    return reviews
