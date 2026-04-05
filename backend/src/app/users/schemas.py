from datetime import datetime

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
