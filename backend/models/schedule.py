from pydantic import BaseModel, Field
from datetime import time
from typing import List, Optional, Literal

class ScheduleEntry(BaseModel):
    schedule_entry_id: int
    team_id: Optional[int]
    field_id: Optional[int]
    parent_schedule_entry_id: Optional[int]
    start_time: time
    end_time: time
    week_day: int

class Schedule(BaseModel):
    schedule_id: int
    club_id: int
    name: str
    facility_id: Optional[int]
    entries: List[ScheduleEntry]


class Constraint(BaseModel):
    team_id: int
    sessions: int
    length: int
    day_of_week: Optional[Literal[0, 1, 2, 3, 4, 5, 6]]
    club_id: Optional[int] = None
    constraint_id: Optional[int] = None
    schedule_entry_id: Optional[int] = None
    required_cost: Optional[int] = None
    required_field: Optional[int] = None  
    start_time: Optional[str] = None
    partial_field: Optional[str] = None
    partial_cost: Optional[int] = None
    partial_time: Optional[int] = None

class GenerateScheduleRequest(BaseModel):
    facility_id: int
    team_ids: List[int]
    constraints: List[Constraint]
    club_id: int
    schedule_name: str = Field(default="Generated Schedule")

