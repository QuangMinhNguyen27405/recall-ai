from uuid import UUID

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.users import crud
from app.users.model import User
from app.users.schemas import UserCreate


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    return await crud.create_user(session, data)


async def list_users(session: AsyncSession) -> list[User]:
    return await crud.list_users(session)


async def get_user(session: AsyncSession, user_id: UUID) -> User:
    user = await crud.get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def delete_user(session: AsyncSession, user_id: UUID) -> None:
    await get_user(session, user_id)
    await crud.delete_user(session, user_id)
