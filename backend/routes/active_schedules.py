from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.user import User
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access
from database.schedules import (
    create_active_schedule,
    get_active_schedules,
    update_active_schedule,
    delete_active_schedule,
    get_active_schedule_club_id
)
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/active-schedules", tags=["active-schedules"])

class ActiveScheduleCreate(BaseModel):
    club_id: int
    schedule_id: int
    start_date: date
    end_date: date

class ActiveScheduleUpdate(BaseModel):
    start_date: date = None
    end_date: date = None
    is_active: bool = None

@router.post("/", response_model=dict)
async def create_active_schedule_route(
    request: ActiveScheduleCreate,
    current_user: User = Depends(get_current_user)
):
    await require_club_access(request.club_id)(current_user)
    
    try:
        active_schedule_id = create_active_schedule(
            request.club_id,
            request.schedule_id,
            request.start_date.isoformat(),
            request.end_date.isoformat()
        )
        return {"active_schedule_id": active_schedule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{club_id}", response_model=List[dict])
async def get_active_schedules_route(
    club_id: int,
    current_user: User = Depends(get_current_user)
):
    await require_club_access(club_id)(current_user)
    return get_active_schedules(club_id)

@router.put("/{active_schedule_id}", response_model=dict)
async def update_active_schedule_route(
    active_schedule_id: int,
    changes: ActiveScheduleUpdate,
    current_user: User = Depends(get_current_user)
):
    club_id = get_active_schedule_club_id(active_schedule_id)
    if not club_id:
        raise HTTPException(status_code=404, detail="Active schedule not found")
        
    await require_club_access(club_id)(current_user)
    
    update_dict = {k: v.isoformat() if isinstance(v, date) else v 
                  for k, v in changes.dict(exclude_unset=True).items()}
    
    if update_active_schedule(active_schedule_id, update_dict):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Update failed")

@router.delete("/{active_schedule_id}", response_model=dict)
async def delete_active_schedule_route(
    active_schedule_id: int,
    current_user: User = Depends(get_current_user)
):
    club_id = get_active_schedule_club_id(active_schedule_id)
    if not club_id:
        raise HTTPException(status_code=404, detail="Active schedule not found")
        
    await require_club_access(club_id)(current_user)
    
    if delete_active_schedule(active_schedule_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Active schedule not found")
