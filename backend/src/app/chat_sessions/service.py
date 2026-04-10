from uuid import UUID

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat_sessions import crud
from app.chat_sessions.model import ChatSession
from app.chat_sessions.schemas import ChatSessionCreate
from app.workspaces import crud as workspaces_crud


async def create_chat_session(
    session: AsyncSession, data: ChatSessionCreate
) -> ChatSession:
    workspace = await workspaces_crud.get_workspace(session, data.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace.user_id != data.user_id:
        raise HTTPException(
            status_code=400,
            detail="Workspace does not belong to the provided user",
        )
    return await crud.create_chat_session(session, data)


async def list_chat_sessions(
    session: AsyncSession,
    user_id: UUID | None = None,
    workspace_id: UUID | None = None,
) -> list[ChatSession]:
    return await crud.list_chat_sessions(
        session, user_id=user_id, workspace_id=workspace_id
    )


async def get_chat_session(session: AsyncSession, chat_session_id: UUID) -> ChatSession:
    chat_session = await crud.get_chat_session(session, chat_session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return chat_session


async def delete_chat_session(session: AsyncSession, chat_session_id: UUID) -> None:
    await get_chat_session(session, chat_session_id)
    await crud.delete_chat_session(session, chat_session_id)
