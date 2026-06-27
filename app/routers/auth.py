from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth import login_user, logout_user, refresh_access_token, register_user
from app.utils.deps import get_current_user
from app.utils.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])

IS_PROD = settings.ENV == "production"


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: Request,
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    await rate_limit(request, max_requests=5, window_seconds=60)
    user = await register_user(data, db)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    await rate_limit(request, max_requests=10, window_seconds=60)
    access_token, refresh_token = await login_user(data.email, data.password, db)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=IS_PROD,
        samesite="none" if IS_PROD else "lax",
        max_age=7 * 24 * 60 * 60,
    )
    return {"access_token": access_token}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str = Depends(lambda req: req.cookies.get("refresh_token")),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    new_access, new_refresh = await refresh_access_token(refresh_token, db)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=IS_PROD,
        samesite="none" if IS_PROD else "lax",
        max_age=7 * 24 * 60 * 60,
    )
    return {"access_token": new_access}


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str = Depends(lambda req: req.cookies.get("refresh_token")),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token:
        await logout_user(refresh_token, db)
    response.delete_cookie(
        "refresh_token",
        secure=IS_PROD,
        samesite="none" if IS_PROD else "lax",
    )
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return user