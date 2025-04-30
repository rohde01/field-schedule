from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from pydantic.types import UUID4

class ScheduleEntry(BaseModel):
    schedule_entry_id: Optional[int] = None
    schedule_id: Optional[int] = None
    uid: UUID4
    team_id: Optional[int] = Field(None, gt=0)
    field_id: Optional[int] = Field(None, gt=0)
    dtstart: datetime
    dtend: datetime
    recurrence_rule: Optional[str] = None
    recurrence_id: Optional[datetime] = None
    exdate: Optional[List[datetime]] = None
    summary: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
