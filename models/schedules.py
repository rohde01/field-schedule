from pydantic import BaseModel
from datetime import time
from typing import List, Optional

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
    entries: List[ScheduleEntry]
