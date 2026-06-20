import uuid
from enum import Enum as PyEnum

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class RequestStatus(str, PyEnum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class ProposalStatus(str, PyEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    budget_min: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    budget_max: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    deadline: Mapped[str | None] = mapped_column(Date)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.open, index=True)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    proposals = relationship("Proposal", back_populates="request", cascade="all, delete-orphan")


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("service_requests.id"), nullable=False, index=True)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    delivery_days: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(Enum(ProposalStatus), default=ProposalStatus.pending)
    created_at: Mapped[str] = mapped_column(server_default=func.now())

    request = relationship("ServiceRequest", back_populates="proposals")