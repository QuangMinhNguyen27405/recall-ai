from datetime import datetime

from sqlmodel import SQLModel


class WorkspaceCreate(SQLModel):
    user_id: int
    name: str


class WorkspaceRead(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int | None
    name: str
    created_at: datetime
