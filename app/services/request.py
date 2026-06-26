import uuid

from app.tasks import run_provider_matching
from app.tasks import run_provider_matching
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.provider import ProviderProfile, ProviderSkill, ProviderStatus
from app.models.request import Proposal, ProposalStatus, RequestStatus, ServiceRequest
from app.models.user import User
from app.schemas.request import ProposalCreate, ServiceRequestCreate


async def create_request(
    data: ServiceRequestCreate,
    client: User,
    db: AsyncSession,
) -> ServiceRequest:
    req = ServiceRequest(
        id=uuid.uuid4(),
        client_id=client.id,
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
        deadline=data.deadline,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    from app.tasks import run_provider_matching
    from app.config import settings
    if settings.REDIS_URL and hasattr(run_provider_matching, 'delay'):
        run_provider_matching.delay(str(req.id))
    else:
         run_provider_matching(str(req.id))

    return req


async def get_client_requests(client_id: uuid.UUID, db: AsyncSession) -> list[ServiceRequest]:
    result = await db.execute(
        select(ServiceRequest)
        .where(ServiceRequest.client_id == client_id)
        .order_by(ServiceRequest.created_at.desc())
    )
    return result.scalars().all()


async def submit_proposal(
    request_id: uuid.UUID,
    data: ProposalCreate,
    provider: User,
    db: AsyncSession,
) -> Proposal:
    req_result = await db.execute(
        select(ServiceRequest).where(ServiceRequest.id == request_id)
    )
    req = req_result.scalar_one_or_none()
    if not req or req.status != RequestStatus.open:
        raise HTTPException(status_code=404, detail="Request not found or not open")

    existing = await db.execute(
        select(Proposal).where(
            Proposal.request_id == request_id,
            Proposal.provider_id == provider.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already submitted a proposal")

    proposal = Proposal(
        id=uuid.uuid4(),
        request_id=request_id,
        provider_id=provider.id,
        cover_letter=data.cover_letter,
        proposed_amount=data.proposed_amount,
        delivery_days=data.delivery_days,
    )
    db.add(proposal)
    await db.commit()
    await db.refresh(proposal)
    return proposal


async def accept_proposal(
    proposal_id: uuid.UUID,
    client: User,
    db: AsyncSession,
) -> Proposal:
    result = await db.execute(
        select(Proposal)
        .where(Proposal.id == proposal_id)
        .options(selectinload(Proposal.request))
    )
    proposal = result.scalar_one_or_none()

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.request.client_id != client.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your request")
    if proposal.request.status != RequestStatus.open:
        raise HTTPException(status_code=400, detail="Request already closed")

    proposal.status = ProposalStatus.accepted
    proposal.request.status = RequestStatus.in_progress

    other = await db.execute(
        select(Proposal).where(
            Proposal.request_id == proposal.request_id,
            Proposal.id != proposal_id,
        )
    )
    for p in other.scalars().all():
        p.status = ProposalStatus.rejected

    await db.commit()
    return proposal


async def get_request_proposals(
    request_id: uuid.UUID,
    client: User,
    db: AsyncSession,
) -> list[Proposal]:
    req_result = await db.execute(
        select(ServiceRequest).where(ServiceRequest.id == request_id)
    )
    req = req_result.scalar_one_or_none()
    if not req or req.client_id != client.id:
        raise HTTPException(status_code=403, detail="Not your request")

    result = await db.execute(
        select(Proposal)
        .where(Proposal.request_id == request_id)
        .options(selectinload(Proposal.request))
    )
    return result.scalars().all()


async def match_providers(request_id: str, db: AsyncSession) -> list[ProviderProfile]:
    req_result = await db.execute(
        select(ServiceRequest).where(ServiceRequest.id == uuid.UUID(request_id))
    )
    req = req_result.scalar_one_or_none()
    if not req:
        return []

    result = await db.execute(
        select(ProviderProfile)
        .where(ProviderProfile.status == ProviderStatus.approved)
        .options(selectinload(ProviderProfile.skills).selectinload(ProviderSkill.skill))
        .order_by(ProviderProfile.avg_rating.desc())
        .limit(5)
    )
    return result.scalars().all()