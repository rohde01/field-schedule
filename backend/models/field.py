from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from enum import Enum

class FieldSize(str, Enum):
    ELEVEN_V_ELEVEN = "11v11"
    EIGHT_V_EIGHT = "8v8"
    FIVE_V_FIVE = "5v5"
    THREE_V_THREE = "3v3"

class FieldType(str, Enum):
    FULL = "full"
    HALF = "half"
    QUARTER = "quarter"

class DayOfWeek(str, Enum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"

class FieldAvailability(BaseModel):
    day_of_week: DayOfWeek
    start_time: str = Field(pattern=r'^([0-1][0-9]|2[0-3]):(00|15|30|45)$')
    end_time: str = Field(pattern=r'^([0-1][0-9]|2[0-3]):(00|15|30|45)$')
    club_id: Optional[int] = Field(gt=0, default=None)

# SubField model (self-referencing)
class SubField(BaseModel):
    field_id: int = Field(gt=0)
    facility_id: int = Field(gt=0)
    club_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)
    field_type: FieldType
    is_active: bool
    parent_field_id: int = Field(gt=0)
    quarter_subfields: Optional[List["SubField"]] = None
    half_subfields: Optional[List["SubField"]] = None

SubField.model_rebuild()

# Main field schema
class Field(BaseModel):
    field_id: int = Field(gt=0)
    facility_id: int = Field(gt=0)
    club_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)
    size: FieldSize
    field_type: FieldType
    is_active: bool
    parent_field_id: Optional[int] = None
    availability: Dict[DayOfWeek, FieldAvailability]
    quarter_subfields: List[SubField] = []
    half_subfields: List[SubField] = []
