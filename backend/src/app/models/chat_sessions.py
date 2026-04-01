import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB

class ChatSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    workspace_id: int
    session_id: str
    messages: dict = Field(sa_type=JSONB, nullable=False)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())