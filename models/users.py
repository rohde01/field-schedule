from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    user_id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "member"

    class Config:
        orm_mode = True
