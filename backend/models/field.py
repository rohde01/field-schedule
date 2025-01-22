from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal, Dict, Annotated

TimeStr = Annotated[str, constr(pattern=r'^([01]\d|2[0-3]):(00|15|30|45)$')]

class FieldAvailability(BaseModel):
    day_of_week: Literal['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_time: TimeStr    # e.g. "16:00"
    end_time: TimeStr      # e.g. "20:00"

class Field(BaseModel):
    field_id: int
    facility_id: int
    name: str
    size: Literal['11v11', '8v8', '5v5', '3v3']
    field_type: Literal['full', 'half', 'quarter']
    parent_field_id: Optional[int]
    is_active: bool = True
    availability: Dict[str, FieldAvailability] = Field(default_factory=dict)
    quarter_subfields: Optional[List['Field']] = Field(default_factory=list)
    half_subfields: Optional[List['Field']] = Field(default_factory=list)