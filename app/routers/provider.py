import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db

from app.models.provider import ProviderStatus, ProviderProfile, ProviderSkill 
from app.models.user import User
from app.schemas.provider import ProviderProfileCreate, ProviderProfileResponse, ProviderSearchResult
from app.services.provider import admin_update_status, create_or_update_profile, get_profile, search_providers
from app.utils.deps import get_current_user, require_admin, require_provider

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("/profile", response_model=ProviderProfileResponse, status_code=201)
async def upsert_profile(
    data: ProviderProfileCreate,
    user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db),
):
    profile = await create_or_update_profile(user, data, db)
    return _format(profile, user)


@router.get("", response_model=list[ProviderSearchResult])
async def search(
    category_slug: str | None = Query(None),
    min_rating: float | None = Query(None),
    max_rate: float | None = Query(None),
    location: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    providers = await search_providers(db, category_slug, min_rating, max_rate, location, page, limit)
    return [_format_search(p) for p in providers]


@router.get("/{provider_id}", response_model=ProviderProfileResponse)
async def get_provider(
    provider_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(provider_id, db)
    return _format(profile, profile.user)


@router.patch("/{provider_id}/approve", response_model=ProviderProfileResponse)
async def approve(
    provider_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    profile = await admin_update_status(provider_id, ProviderStatus.approved, admin, db)
    return _format(profile, profile.user if hasattr(profile, 'user') else None)


@router.patch("/{provider_id}/suspend", response_model=ProviderProfileResponse)
async def suspend(
    provider_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    profile = await admin_update_status(provider_id, ProviderStatus.suspended, admin, db)
    return _format(profile, profile.user if hasattr(profile, 'user') else None)


@router.get("/admin/all", response_model=list[ProviderProfileResponse])
async def all_providers_admin(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProviderProfile)
        .options(
            selectinload(ProviderProfile.skills).selectinload(ProviderSkill.skill),
            selectinload(ProviderProfile.user)
        )
        .order_by(ProviderProfile.created_at.desc())
    )
    profiles = result.scalars().all()
    return [_format(p, p.user) for p in profiles]
# ---------------------------------------------


def _format(profile, user) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "bio": profile.bio,
        "tagline": profile.tagline,
        "hourly_rate": profile.hourly_rate,
        "years_experience": profile.years_experience,
        "location": profile.location,
        "status": profile.status,
        "avg_rating": profile.avg_rating,
        "total_reviews": profile.total_reviews,
        "full_name": user.full_name if user else None,
        "email": user.email if user else None,
        "skills": [ps.skill.name for ps in profile.skills] if profile.skills else [],
    }


def _format_search(profile) -> dict:
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "tagline": profile.tagline,
        "hourly_rate": profile.hourly_rate,
        "location": profile.location,
        "avg_rating": profile.avg_rating,
        "total_reviews": profile.total_reviews,
        "full_name": profile.user.full_name if profile.user else None,
        "skills": [ps.skill.name for ps in profile.skills] if profile.skills else [],
    }