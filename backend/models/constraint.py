from pydantic import BaseModel
from typing import Optional, Literal

class Constraint(BaseModel):
    team_id: int
    sessions: int
    start_time: Optional[str] = None
    length: int
    day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None
    required_cost: Optional[int] = None
    required_field: Optional[int] = None


    