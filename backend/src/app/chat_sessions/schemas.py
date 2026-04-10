from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class ChatSessionCreate(SQLModel):
    user_id: UUID
    workspace_id: UUID
    session_id: str
    messages: dict


class ChatSessionRead(SQLModel):
    model_config = {"from_attributes": True}

    id: UUID
    user_id: UUID | None
    workspace_id: UUID | None
    session_id: str
    messages: dict
    created_at: datetime
    updated_at: datetime
