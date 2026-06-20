import uuid
from enum import Enum as PyEnum

from sqlalchemy import DECIMAL, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ProviderStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    suspended = "suspended"


class ProviderProfile(Base):
    __tablename__ = "provider_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    tagline: Mapped[str | None] = mapped_column(String(150))
    hourly_rate: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    years_experience: Mapped[int | None] = mapped_column(Integer)
    location: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[ProviderStatus] = mapped_column(Enum(ProviderStatus), default=ProviderStatus.pending, index=True)
    avg_rating: Mapped[float] = mapped_column(DECIMAL(3, 2), default=0.00, index=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    response_time_hours: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    user = relationship("User", back_populates="provider_profile")
    skills = relationship("ProviderSkill", back_populates="provider", cascade="all, delete-orphan")


class ProviderSkill(Base):
    __tablename__ = "provider_skills"

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("provider_profiles.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    provider = relationship("ProviderProfile", back_populates="skills")
    skill = relationship("Skill")