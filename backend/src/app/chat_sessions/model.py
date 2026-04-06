from datetime import datetime

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

    user: "User" = Relationship(back_populates="chat_sessions")  # pyright: ignore[reportUndefinedVariable]
    workspace: "Workspace" = Relationship(back_populates="chat_sessions")  # pyright: ignore[reportUndefinedVariable]

    session_id: str = Field(nullable=False)
    messages: dict = Field(sa_type=JSONB, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
