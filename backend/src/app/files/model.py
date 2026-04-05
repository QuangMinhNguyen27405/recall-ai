from __future__ import annotations

import enum
from datetime import datetime

from app.users import User
from app.workspaces.model import Workspace
from sqlmodel import Field, Relationship, SQLModel


class FileStatus(str, enum.Enum):
    unprocessed = "unprocessed"
    processing = "processing"
    ready = "ready"
    error = "error"


class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    workspace_id: int | None = Field(
        default=None, foreign_key="workspace.id", ondelete="CASCADE"
    )

    user: "User | None" = Relationship(back_populates="files")
    workspace: "Workspace | None" = Relationship(back_populates="files")

    name: str = Field(nullable=False)
    s3_key: str = Field(nullable=False)
    status: FileStatus = Field(default=FileStatus.processing)
    error_reason: str | None = None
    ingested_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
