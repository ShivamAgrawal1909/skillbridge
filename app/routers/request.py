import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.request import RequestStatus, ServiceRequest
from app.models.user import User
from app.schemas.request import (
    ProposalCreate,
    ProposalResponse,
    ServiceRequestCreate,
    ServiceRequestResponse,
)
from app.services.request import (
    accept_proposal,
    create_request,
    get_client_requests,
    get_request_proposals,
    submit_proposal,
)
from app.utils.deps import get_current_user, require_client, require_provider

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=ServiceRequestResponse, status_code=201)
async def post_request(
    data: ServiceRequestCreate,
    client: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    return await create_request(data, client, db)


@router.get("/open", response_model=list[ServiceRequestResponse])
async def open_requests(
    provider: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ServiceRequest)
        .where(ServiceRequest.status == RequestStatus.open)
        .order_by(ServiceRequest.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()


@router.get("", response_model=list[ServiceRequestResponse])
async def my_requests(
    client: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    return await get_client_requests(client.id, db)


@router.post("/{request_id}/proposals", response_model=ProposalResponse, status_code=201)
async def propose(
    request_id: uuid.UUID,
    data: ProposalCreate,
    provider: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db),
):
    proposal = await submit_proposal(request_id, data, provider, db)
    return {
        "id": proposal.id,
        "request_id": proposal.request_id,
        "provider_id": proposal.provider_id,
        "cover_letter": proposal.cover_letter,
        "proposed_amount": proposal.proposed_amount,
        "delivery_days": proposal.delivery_days,
        "status": proposal.status,
        "provider_name": provider.full_name,
    }


@router.get("/{request_id}/proposals", response_model=list[ProposalResponse])
async def list_proposals(
    request_id: uuid.UUID,
    client: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    proposals = await get_request_proposals(request_id, client, db)
    result = []
    for p in proposals:
        user_result = await db.execute(
            select(User).where(User.id == p.provider_id)
        )
        provider_user = user_result.scalar_one_or_none()
        result.append({
            "id": p.id,
            "request_id": p.request_id,
            "provider_id": p.provider_id,
            "cover_letter": p.cover_letter,
            "proposed_amount": p.proposed_amount,
            "delivery_days": p.delivery_days,
            "status": p.status,
            "provider_name": provider_user.full_name if provider_user else None,
        })
    return result


@router.patch("/proposals/{proposal_id}/accept", response_model=ProposalResponse)
async def accept(
    proposal_id: uuid.UUID,
    client: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    proposal = await accept_proposal(proposal_id, client, db)
    return {
        "id": proposal.id,
        "request_id": proposal.request_id,
        "provider_id": proposal.provider_id,
        "cover_letter": proposal.cover_letter,
        "proposed_amount": proposal.proposed_amount,
        "delivery_days": proposal.delivery_days,
        "status": proposal.status,
        "provider_name": None,
    }