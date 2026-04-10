from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class WorkspaceCreate(SQLModel):
    user_id: UUID
    name: str


class WorkspaceRead(SQLModel):
    model_config = {"from_attributes": True}

    id: UUID
    user_id: UUID | None
    name: str
    created_at: datetime
