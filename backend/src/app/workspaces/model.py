from __future__ import annotations

from datetime import datetime

from app.chat_sessions import ChatSession
from app.files.model import File
from app.users.model import User
from sqlmodel import Field, Relationship, SQLModel


class Workspace(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )

    user: "User | None" = Relationship(back_populates="workspaces")
    files: list["File"] = Relationship(back_populates="workspace", cascade_delete=True)
    chat_sessions: list["ChatSession"] = Relationship(
        back_populates="workspace", cascade_delete=True
    )

    name: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
