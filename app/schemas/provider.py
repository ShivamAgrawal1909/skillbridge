import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.models.provider import ProviderStatus


class ProviderProfileCreate(BaseModel):
    bio: str | None = None
    tagline: str | None = None
    hourly_rate: Decimal | None = None
    years_experience: int | None = None
    location: str | None = None
    skill_ids: list[uuid.UUID] = []


class ProviderProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    bio: str | None
    tagline: str | None
    hourly_rate: Decimal | None
    years_experience: int | None
    location: str | None
    status: ProviderStatus
    avg_rating: Decimal
    total_reviews: int
    full_name: str | None = None
    email: str | None = None
    skills: list[str] = []

    model_config = {"from_attributes": True}


class ProviderSearchResult(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tagline: str | None
    hourly_rate: Decimal | None
    location: str | None
    avg_rating: Decimal
    total_reviews: int
    full_name: str | None = None
    skills: list[str] = []

    model_config = {"from_attributes": True}