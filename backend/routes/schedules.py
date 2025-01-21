'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from main import generate_schedule
from database.constraints import Constraint as ConstraintModel
from database.schedules import get_club_schedules, delete_schedule, get_schedule_club_id
from backend.models.schedule import Schedule
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access
from backend.models.user import User
from database.constraints import get_constraints
from backend.models.schedule import GenerateScheduleRequest, Constraint

router = APIRouter(prefix="/schedules", tags=["schedules"])


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

@router.get("/{club_id}/constraints", response_model=List[Constraint])
async def fetch_club_constraints(
    club_id: int,
    current_user: User = Depends(get_current_user)
):
    print(f"Fetching constraints for club_id: {club_id}")
    try:
        await require_club_access(club_id)(current_user)
        
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
            response.append(Constraint(**constraint_dict))
            
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