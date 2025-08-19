from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: str
    phone: str
    name: str | None = None
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True