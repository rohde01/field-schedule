'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from main import generate_schedule
from database.constraints import Constraint as ConstraintModel
from database.schedules import get_schedule
from models.schedules import Schedule
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access
from models.users import User

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

@router.post("/generate", response_model=dict)
async def generate_schedule_route(
    request: GenerateScheduleRequest,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(require_club_access(lambda r: r.club_id))
):
    try:
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

@router.get("/{schedule_id}", response_model=Schedule)
async def fetch_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user)
):
    schedule_data = get_schedule(schedule_id)
    if not schedule_data:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    _ = await require_club_access(schedule_data['club_id'])(current_user)
    
    return schedule_data

