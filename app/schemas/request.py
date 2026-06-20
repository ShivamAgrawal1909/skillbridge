import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.request import ProposalStatus, RequestStatus


class ServiceRequestCreate(BaseModel):
    title: str
    description: str
    category_id: uuid.UUID
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    deadline: date | None = None


class ServiceRequestResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    category_id: uuid.UUID
    title: str
    description: str
    budget_min: Decimal | None
    budget_max: Decimal | None
    deadline: date | None
    status: RequestStatus

    model_config = {"from_attributes": True}


class ProposalCreate(BaseModel):
    cover_letter: str
    proposed_amount: Decimal
    delivery_days: int


class ProposalResponse(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    provider_id: uuid.UUID
    cover_letter: str
    proposed_amount: Decimal
    delivery_days: int
    status: ProposalStatus
    provider_name: str | None = None

    model_config = {"from_attributes": True}