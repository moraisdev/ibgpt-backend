from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.services.auth import (
    authenticate_user,
    create_access_token,
    register_user,
    refresh_access_token_service,
)
from app.schemas.auth import UserCreate, UserResponse, TokenResponse, LoginForm
from app.config.config import settings
from datetime import timedelta

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user_endpoint(
    user: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        new_user = await register_user(session, user.dict())
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao registrar usuário: {e}",
        )


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: LoginForm, session: AsyncSession = Depends(get_async_session)
):
    user = await authenticate_user(session, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token_endpoint(refresh_token: str):
    return await refresh_access_token_service(refresh_token)
