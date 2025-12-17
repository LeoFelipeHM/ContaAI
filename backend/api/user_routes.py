from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from database.session import get_session
from database.data_module import User
from auth.security import hash_password

user_router = APIRouter(prefix="/users", tags=["Users"])


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    timezone: str | None = "America/Sao_Paulo"


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    timezone: str | None = None


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    timezone: str
    created_at: datetime
    updated_at: datetime


@user_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User).where(User.email == data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        timezone=data.timezone,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.password_hash = hash_password(data.password)
    if data.timezone is not None:
        user.timezone = data.timezone

    user.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(user)

    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT) # Tem que atualizar essa função pra usar soft delete (mudar apenas o status)
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await session.delete(user)
    await session.commit()
