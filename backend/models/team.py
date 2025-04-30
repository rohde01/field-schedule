from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

ValidFieldSize = Literal[125, 250, 500, 1000]

class Gender(str, Enum):
    BOYS = "boys"
    GIRLS = "girls"

class Team(BaseModel):
    team_id: int = Field(gt=0)
    name: str = Field(min_length=1)
    year: str = Field(pattern=r'^U([4-9]|1[0-9]|2[0-4])$')
    club_id: int = Field(gt=0)
    gender: Gender
    is_academy: bool
    minimum_field_size: ValidFieldSize
    preferred_field_size: Optional[ValidFieldSize] = None
    level: int = Field(ge=1, le=5)
    is_active: bool = True
    weekly_trainings: int = Field(ge=1, le=7)
