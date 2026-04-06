from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class Workspace(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )

    user: "User" = Relationship(back_populates="workspaces")  # pyright: ignore[reportUndefinedVariable]
    files: list["File"] = Relationship(back_populates="workspace", cascade_delete=True)  # pyright: ignore[reportUndefinedVariable]
    chat_sessions: list["ChatSession"] = Relationship(  # pyright: ignore[reportUndefinedVariable]
        back_populates="workspace", cascade_delete=True
    )

    name: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
