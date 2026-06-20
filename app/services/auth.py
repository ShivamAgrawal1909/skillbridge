import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import RefreshToken
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.utils.security import (
    create_access_token,
    generate_refresh_token,
    generate_verification_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.config import settings


async def register_user(data: RegisterRequest, db: AsyncSession) -> User:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        phone=data.phone,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    db.add(AuditLog(
        id=uuid.uuid4(),
        user_id=user.id,
        action="register",
        resource="user",
        detail=f"New {data.role} registered",
    ))

    await db.commit()
    return user


async def login_user(email: str, password: str, db: AsyncSession) -> tuple[str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")

    access_token = create_access_token(str(user.id), user.role)

    raw_refresh = generate_refresh_token()
    db.add(RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))

    db.add(AuditLog(
        id=uuid.uuid4(),
        user_id=user.id,
        action="login",
        resource="user",
    ))

    await db.commit()
    return access_token, raw_refresh


async def refresh_access_token(raw_refresh: str, db: AsyncSession) -> tuple[str, str]:
    token_hash = hash_token(raw_refresh)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    token.revoked = True

    user_result = await db.execute(select(User).where(User.id == token.user_id))
    user = user_result.scalar_one()

    new_access = create_access_token(str(user.id), user.role)
    new_raw_refresh = generate_refresh_token()

    db.add(RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hash_token(new_raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))

    await db.commit()
    return new_access, new_raw_refresh


async def logout_user(raw_refresh: str, db: AsyncSession):
    token_hash = hash_token(raw_refresh)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token = result.scalar_one_or_none()
    if token:
        token.revoked = True
        await db.commit()