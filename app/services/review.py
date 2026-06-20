import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import ProviderProfile
from app.models.request import RequestStatus, ServiceRequest
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate


async def submit_review(
    request_id: uuid.UUID,
    reviewee_id: uuid.UUID,
    data: ReviewCreate,
    reviewer: User,
    db: AsyncSession,
) -> Review:
    req_result = await db.execute(
        select(ServiceRequest).where(ServiceRequest.id == request_id)
    )
    req = req_result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != RequestStatus.completed:
        raise HTTPException(status_code=400, detail="Can only review completed jobs")

    existing = await db.execute(
        select(Review).where(
            Review.request_id == request_id,
            Review.reviewer_id == reviewer.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already reviewed this job")

    review = Review(
        id=uuid.uuid4(),
        request_id=request_id,
        reviewer_id=reviewer.id,
        reviewee_id=reviewee_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    await db.flush()

    # update provider avg_rating
    avg_result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(
            Review.reviewee_id == reviewee_id
        )
    )
    avg, count = avg_result.one()

    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == reviewee_id)
    )
    provider = provider_result.scalar_one_or_none()
    if provider:
        provider.avg_rating = round(float(avg), 2)
        provider.total_reviews = count

    await db.commit()
    await db.refresh(review)
    return review


async def get_provider_reviews(reviewee_id: uuid.UUID, db: AsyncSession) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.reviewee_id == reviewee_id)
        .order_by(Review.created_at.desc())
    )
    return result.scalars().all()