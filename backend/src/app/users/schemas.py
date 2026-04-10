from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    model_config = {"from_attributes": True}

    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
