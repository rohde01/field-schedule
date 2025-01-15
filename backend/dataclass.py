from dataclasses import dataclass, field
from typing import Dict, List, Optional
from typing import Literal

@dataclass
class FieldAvailability:
    day_of_week: Literal['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    start_time: str    # e.g. "16:00"
    end_time: str      # e.g. "20:00"

@dataclass
class Field:
    field_id: int
    facility_id: int
    name: str
    size: str                  # '11v11', '8v8', '5v5', '3v3'
    field_type: str            # 'full', 'half', 'quarter'
    parent_field_id: Optional[int]
    is_active: bool = True
    availability: Dict[str, FieldAvailability] = field(default_factory=dict)
    quarter_subfields: List['Field'] = field(default_factory=list)
    half_subfields: List['Field'] = field(default_factory=list)

@dataclass
class Constraint:
    team_id: int
    sessions: int
    length: int               # in 15-minute blocks
    required_cost: Optional[str]        # '125','250','500','1000'
    required_field: Optional[int]       # A specific field_id to be used in the session. If specified, required_size is ignored.
    start_time: Optional[str] = None  # optional fixed start time

@dataclass
class Team:
    team_id: int
    name: str
    year: str
    club_id: int
    gender: str
    is_academy: bool
    minimum_field_size: int
    preferred_field_size: Optional[int]
    level: int
    is_active: bool
    weekly_trainings: int
    training_length: Optional[int]