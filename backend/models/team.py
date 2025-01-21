from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
import re

class Team(BaseModel):
    team_id: Optional[int]
    name: str
    year: str = Field(..., pattern=r"^U([4-9]|1[0-9]|2[0-4])$")
    club_id: int
    gender: Literal["boys", "girls"]
    is_academy: bool
    minimum_field_size: Literal[125, 250, 500, 1000]
    preferred_field_size: Literal[125, 250, 500, 1000]
    level: Literal[1, 2, 3, 4, 5]
    is_active: bool = True
    weekly_trainings: Literal[1, 2, 3, 4, 5, 6, 7]
    training_length: Optional[int] = None