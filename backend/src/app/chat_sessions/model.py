from __future__ import annotations

from datetime import datetime

from app.users import User
from app.workspaces.model import Workspace
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


class ChatSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    workspace_id: int | None = Field(
        default=None, foreign_key="workspace.id", ondelete="CASCADE"
    )

    user: "User | None" = Relationship(back_populates="chat_sessions")
    workspace: "Workspace | None" = Relationship(back_populates="chat_sessions")

    session_id: str = Field(nullable=False)
    messages: dict = Field(sa_type=JSONB, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
