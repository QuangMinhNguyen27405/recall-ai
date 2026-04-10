from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat_sessions.model import ChatSession
from app.chat_sessions.schemas import ChatSessionCreate


async def create_chat_session(
    session: AsyncSession, data: ChatSessionCreate
) -> ChatSession:
    chat_session = ChatSession.model_validate(data)
    session.add(chat_session)
    await session.commit()
    await session.refresh(chat_session)
    return chat_session


async def get_chat_session(
    session: AsyncSession, chat_session_id: UUID
) -> ChatSession | None:
    return await session.get(ChatSession, chat_session_id)


async def list_chat_sessions(
    session: AsyncSession,
    user_id: UUID | None = None,
    workspace_id: UUID | None = None,
) -> list[ChatSession]:
    statement = select(ChatSession)
    if user_id is not None:
        statement = statement.where(ChatSession.user_id == user_id)
    if workspace_id is not None:
        statement = statement.where(ChatSession.workspace_id == workspace_id)
    result = await session.exec(statement)
    return result.all()


async def delete_chat_session(session: AsyncSession, chat_session: ChatSession) -> None:
    await session.delete(chat_session)
    await session.commit()
