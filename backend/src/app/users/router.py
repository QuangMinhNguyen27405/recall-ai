from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.users import service
from app.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserRead:
    user = await service.create_user(session, payload)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)) -> list[UserRead]:
    users = await service.list_users(session)
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_session)) -> UserRead:
    user = await service.get_user(session, user_id)
    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_session)) -> None:
    await service.delete_user(session, user_id)
