from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.users.model import User
from app.users.schemas import UserCreate
from uuid import UUID


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    user = User.model_validate(data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def list_users(session: AsyncSession) -> list[User]:
    result = await session.exec(select(User))
    return result.all()


async def delete_user(session: AsyncSession, user_id: UUID) -> None:
    user = await session.get(User, user_id)
    if user is None:
        return
    await session.delete(user)
    await session.commit()
