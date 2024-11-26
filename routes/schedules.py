from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from main import generate_schedule
from database.constraints import Constraint as ConstraintModel
from database.schedules import get_schedule_entries

router = APIRouter(prefix="/schedules", tags=["schedules"])

class ConstraintSchema(BaseModel):
    team_id: int
    required_size: Optional[str] = None
    subfield_type: Optional[str] = None
    required_cost: Optional[int] = None
    sessions: int = Field(default=1)
    length: int = Field(default=1)
    partial_ses_space_size: Optional[str] = None
    partial_ses_space_cost: Optional[int] = None
    partial_ses_time: Optional[int] = None
    start_time: Optional[str] = None

class GenerateScheduleRequest(BaseModel):
    facility_id: int
    team_ids: List[int]
    constraints: List[ConstraintSchema]
    club_id: int
    schedule_name: str = Field(default="Generated Schedule")

@router.post("/generate_schedule")
async def generate_schedule_route(request: GenerateScheduleRequest):
    try:
        # Convert constraints to ConstraintModel instances
        constraints_list = [ConstraintModel(**constraint.dict()) for constraint in request.constraints]
        schedule_id = generate_schedule(
            facility_id=request.facility_id,
            team_ids=request.team_ids,
            constraints_list=constraints_list,
            club_id=request.club_id,
            schedule_name=request.schedule_name
        )
        return {"schedule_id": schedule_id}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{schedule_id}/entries")
async def get_entries(schedule_id: int) -> List[dict]:
    try:
        entries = get_schedule_entries(schedule_id)
        return [
            {
                "team_id": entry[0],
                "field_id": entry[1],
                "session_start": entry[2],
                "session_end": entry[3],
                "parent_schedule_entry_id": entry[4],
            }
            for entry in entries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
