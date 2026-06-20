import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review import get_provider_reviews, submit_review
from app.utils.deps import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    request_id: uuid.UUID,
    reviewee_id: uuid.UUID,
    data: ReviewCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await submit_review(request_id, reviewee_id, data, user, db)


@router.get("/provider/{reviewee_id}", response_model=list[ReviewResponse])
async def provider_reviews(
    reviewee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await get_provider_reviews(reviewee_id, db)