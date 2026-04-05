from datetime import datetime

from sqlmodel import SQLModel


class ChatSessionCreate(SQLModel):
    user_id: int
    workspace_id: int
    session_id: str
    messages: dict


class ChatSessionRead(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int | None
    workspace_id: int | None
    session_id: str
    messages: dict
    created_at: datetime
    updated_at: datetime
