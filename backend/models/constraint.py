from pydantic import BaseModel, Field
from typing import Optional, Literal
import re
from uuid import UUID

class Constraint(BaseModel):
    uid: UUID
    team_id: int
    start_time: Optional[str] = Field(None, pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')  # HH:MM format
    length: int
    day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None
    required_cost: Optional[Literal[125, 250, 500, 1000]] = None
    field_id: Optional[int] = None


