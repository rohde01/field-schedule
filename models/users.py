from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    user_id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "member"
    primary_club_id: Optional[int] = None