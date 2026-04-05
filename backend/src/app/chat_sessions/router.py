from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.chat_sessions import crud
from app.chat_sessions.schemas import ChatSessionCreate, ChatSessionRead
from app.db.session import get_session

router = APIRouter(prefix="/chat-sessions", tags=["chat-sessions"])


@router.post("", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatSessionCreate, session: AsyncSession = Depends(get_session)
) -> ChatSessionRead:
    chat_session = await crud.create_chat_session(session, payload)
    return ChatSessionRead.model_validate(chat_session)


@router.get("", response_model=list[ChatSessionRead])
async def list_chat_sessions(
    user_id: int | None = Query(default=None),
    workspace_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[ChatSessionRead]:
    sessions = await crud.list_chat_sessions(
        session, user_id=user_id, workspace_id=workspace_id
    )
    return [ChatSessionRead.model_validate(chat_session) for chat_session in sessions]


@router.get("/{chat_session_id}", response_model=ChatSessionRead)
async def get_chat_session(
    chat_session_id: int, session: AsyncSession = Depends(get_session)
) -> ChatSessionRead:
    chat_session = await crud.get_chat_session(session, chat_session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return ChatSessionRead.model_validate(chat_session)


@router.delete("/{chat_session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    chat_session_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    chat_session = await crud.get_chat_session(session, chat_session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    await crud.delete_chat_session(session, chat_session)
