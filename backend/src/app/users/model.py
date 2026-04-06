from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    workspaces: list["Workspace"] = Relationship(  # pyright: ignore[reportUndefinedVariable]
        back_populates="user", cascade_delete=True
    )
    files: list["File"] = Relationship(back_populates="user", cascade_delete=True)  # pyright: ignore[reportUndefinedVariable]
    chat_sessions: list["ChatSession"] = Relationship(  # pyright: ignore[reportUndefinedVariable]
        back_populates="user", cascade_delete=True
    )

    username: str = Field(nullable=False)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
