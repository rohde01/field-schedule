from pydantic import BaseModel
from typing import Optional, Literal

class BaseConstraint(BaseModel):
    team_id: int
    sessions: int
    length: int
    required_cost: Optional[int] = None
    
class SpecificConstraint(BaseModel):
    team_id: int
    start_time: Optional[str] = None
    length: int
    day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None
    required_field: Optional[int] = None


