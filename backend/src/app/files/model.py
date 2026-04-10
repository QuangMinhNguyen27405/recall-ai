import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class FileStatus(str, enum.Enum):
    unprocessed = "unprocessed"
    processing = "processing"
    ready = "ready"
    error = "error"


class File(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    workspace_id: UUID | None = Field(
        default=None, foreign_key="workspace.id", ondelete="CASCADE"
    )

    user: "User" = Relationship(back_populates="files")  # pyright: ignore[reportUndefinedVariable]
    workspace: "Workspace" = Relationship(back_populates="files")  # pyright: ignore[reportUndefinedVariable]

    name: str = Field(nullable=False)
    s3_key: str = Field(nullable=False)
    status: FileStatus = Field(default=FileStatus.processing)
    error_reason: str | None = None
    ingested_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
