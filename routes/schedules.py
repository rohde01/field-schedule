'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from main import generate_schedule
from database.constraints import Constraint as ConstraintModel
from database.schedules import get_club_schedules, delete_schedule, get_schedule_club_id
from models.schedules import Schedule
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access
from models.users import User

router = APIRouter(prefix="/schedules", tags=["schedules"])

class ConstraintSchema(BaseModel):
    team_id: int
    club_id: Optional[int] = None
    required_size: Optional[str] = None
    subfield_type: Optional[str] = None
    required_cost: Optional[int] = None
    sessions: int = Field(default=1)
    length: int = Field(default=1)
    partial_ses_space_size: Optional[str] = None
    partial_ses_space_cost: Optional[int] = None
    partial_ses_time: Optional[int] = None
    start_time: Optional[str] = None

class ConstraintResponse(BaseModel):
    team_id: int
    required_size: Optional[str]
    subfield_type: Optional[str]
    required_cost: Optional[int]
    sessions: int
    length: int
    partial_ses_space_size: Optional[str]
    partial_ses_space_cost: Optional[int]
    partial_ses_time: Optional[int]
    start_time: Optional[str]

class GenerateScheduleRequest(BaseModel):
    facility_id: int
    team_ids: List[int]
    constraints: List[ConstraintSchema]
    club_id: int
    schedule_name: str = Field(default="Generated Schedule")

@router.post("/generate", response_model=dict)
async def generate_schedule_route(
    request: GenerateScheduleRequest,
    current_user: User = Depends(get_current_user)
):
    await require_club_access(request.club_id)(current_user)
    
    try:
        constraints_list = [
            ConstraintModel(
                **{**constraint.dict(), "club_id": request.club_id}
            ) 
            for constraint in request.constraints
        ]
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

@router.get("/{club_id}/schedules", response_model=List[Schedule])
async def fetch_club_schedules(
    club_id: int,
    current_user: User = Depends(get_current_user)
):
    await require_club_access(club_id)(current_user)
    
    schedules = get_club_schedules(club_id)
    return schedules

@router.get("/{club_id}/constraints", response_model=List[ConstraintResponse])
async def fetch_club_constraints(
    club_id: int,
    current_user: User = Depends(get_current_user)
):
    print(f"Fetching constraints for club_id: {club_id}")
    try:
        await require_club_access(club_id)(current_user)
        
        from database.constraints import get_constraints
        constraints = get_constraints(club_id)
        
        if not constraints:
            return []
            
        response = []
        for constraint in constraints:
            constraint_dict = {
                k: v for k, v in constraint.__dict__.items() if k != 'club_id'
            }
            if constraint_dict.get('start_time'):
                constraint_dict['start_time'] = constraint_dict['start_time'].strftime('%H:%M:%S')
            response.append(ConstraintResponse(**constraint_dict))
            
        return response
    except Exception as e:
        print(f"Error fetching constraints: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching constraints: {str(e)}"
        )

@router.delete("/delete/{schedule_id}", response_model=dict)
async def delete_schedule_route(
    schedule_id: int,
    current_user: User = Depends(get_current_user)
) -> dict:
    try:
        club_id = get_schedule_club_id(schedule_id)
        
        if club_id is None:
            raise HTTPException(status_code=404, detail="Schedule not found")
            
        await require_club_access(club_id)(current_user)
        
        success = delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
            
        return {
            "success": True,
            "message": "Schedule deleted successfully",
            "action": "delete",
            "schedule_id": schedule_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))