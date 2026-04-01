import datetime
from sqlmodel import Field, SQLModel

class Workspace(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  
    user_id: int
    name: str
    created_at: datetime = Field(default=datetime.now())