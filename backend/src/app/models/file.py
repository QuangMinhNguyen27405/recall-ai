import datetime
from sqlmodel import Field, SQLModel, enum

class FileStatus(str, enum.Enum):
    unprocessed = "unprocessed"
    processing = "processing"
    ready = "ready"
    error = "error"

class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    s3_key: str
    workspace_id: int
    status: FileStatus = Field(default=FileStatus.processing)
    error_reason: str | None = None
    ingested_at: datetime | None = None
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())