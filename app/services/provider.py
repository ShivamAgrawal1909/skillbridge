import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog
from app.models.provider import ProviderProfile, ProviderSkill, ProviderStatus
from app.models.user import User
from app.schemas.provider import ProviderProfileCreate


async def create_or_update_profile(
    user: User,
    data: ProviderProfileCreate,
    db: AsyncSession,
) -> ProviderProfile:
    result = await db.execute(
        select(ProviderProfile)
        .where(ProviderProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = ProviderProfile(id=uuid.uuid4(), user_id=user.id)
        db.add(profile)
        await db.flush()

    profile.bio = data.bio
    profile.tagline = data.tagline
    profile.hourly_rate = data.hourly_rate
    profile.years_experience = data.years_experience
    profile.location = data.location

    await db.execute(
        delete(ProviderSkill).where(ProviderSkill.provider_id == profile.id)
    )
    for skill_id in data.skill_ids:
        db.add(ProviderSkill(provider_id=profile.id, skill_id=skill_id))

    await db.commit()

    result = await db.execute(
        select(ProviderProfile)
        .where(ProviderProfile.id == profile.id)
        .options(selectinload(ProviderProfile.skills).selectinload(ProviderSkill.skill))
    )
    return result.scalar_one()


async def get_profile(provider_id: uuid.UUID, db: AsyncSession) -> ProviderProfile:
    result = await db.execute(
        select(ProviderProfile)
        .where(ProviderProfile.id == provider_id)
        .options(
            selectinload(ProviderProfile.skills).selectinload(ProviderSkill.skill),
            selectinload(ProviderProfile.user)
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return profile


async def search_providers(
    db: AsyncSession,
    category_slug: str | None = None,
    min_rating: float | None = None,
    max_rate: float | None = None,
    location: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> list[ProviderProfile]:
    query = (
        select(ProviderProfile)
        .where(ProviderProfile.status == ProviderStatus.approved)
        .options(
            selectinload(ProviderProfile.skills).selectinload(ProviderSkill.skill),
            selectinload(ProviderProfile.user)
        )
        .order_by(ProviderProfile.avg_rating.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if category_slug:
        from app.models.category import Category, Skill
        skill_subq = select(ProviderSkill.provider_id).join(
            Skill, ProviderSkill.skill_id == Skill.id
        ).join(
            Category, Skill.category_id == Category.id
        ).where(Category.slug == category_slug)
        query = query.where(ProviderProfile.id.in_(skill_subq))

    if min_rating:
        query = query.where(ProviderProfile.avg_rating >= min_rating)
    if max_rate:
        query = query.where(ProviderProfile.hourly_rate <= max_rate)
    if location:
        query = query.where(ProviderProfile.location.ilike(f"%{location}%"))

    result = await db.execute(query)
    return result.scalars().all()


async def admin_update_status(
    provider_id: uuid.UUID,
    new_status: ProviderStatus,
    admin: User,
    db: AsyncSession,
) -> ProviderProfile:
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == provider_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    profile.status = new_status
    db.add(AuditLog(
        id=uuid.uuid4(),
        user_id=admin.id,
        action=f"provider_{new_status}",
        resource="provider_profile",
        detail=str(provider_id),
    ))
    await db.commit()

    result = await db.execute(
        select(ProviderProfile)
        .where(ProviderProfile.id == provider_id)
        .options(
            selectinload(ProviderProfile.skills).selectinload(ProviderSkill.skill),
            selectinload(ProviderProfile.user)
        )
    )
    return result.scalar_one()