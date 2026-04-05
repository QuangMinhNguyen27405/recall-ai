from datetime import datetime

from sqlmodel import SQLModel

from app.files.model import FileStatus


class FileCreate(SQLModel):
    user_id: int
    workspace_id: int
    name: str
    s3_key: str


class FileRead(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int | None
    workspace_id: int | None
    name: str
    s3_key: str
    status: FileStatus
    error_reason: str | None
    ingested_at: datetime | None
    created_at: datetime
    updated_at: datetime
