from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.files.model import FileStatus


class FileCreate(SQLModel):
    user_id: UUID
    workspace_id: UUID
    name: str
    s3_key: str


class FileRead(SQLModel):
    model_config = {"from_attributes": True}

    id: UUID
    user_id: UUID | None
    workspace_id: UUID | None
    name: str
    s3_key: str
    status: FileStatus
    error_reason: str | None
    ingested_at: datetime | None
    created_at: datetime
    updated_at: datetime
