'''
Filename: schedules.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from main import generate_schedule
from models.schedule import Schedule
from models.schedule import GenerateScheduleRequest, Constraint
from models.schedule import CreateScheduleEntry, ScheduleEntryCreate

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

@router.put("/entry/{entry_id}")
async def update_entry(
    entry_id: int,
    changes: dict,
    current_user: User = Depends(get_current_user)
):
    schedule_id = get_schedule_entry_schedule_id(entry_id)
    if not schedule_id:
        raise HTTPException(status_code=404, detail="Schedule entry not found")
        
    club_id = get_schedule_club_id(schedule_id)
    if not club_id:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    await require_club_access(club_id)(current_user)
    
    success = update_schedule_entry(entry_id, changes)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Failed to update schedule entry"
        )
        
    return {"success": True}

@router.post("/entry")
async def create_entry(
    request: CreateScheduleEntry,
    current_user: User = Depends(get_current_user)
):
    club_id = get_schedule_club_id(request.schedule_id)
    if not club_id:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    await require_club_access(club_id)(current_user)
    
    try:
        entry_data = ScheduleEntryCreate(**request.entry)
        entry_id = create_schedule_entry(request.schedule_id, entry_data.dict())
        return {"success": True, "schedule_entry_id": entry_id} if entry_id else \
               HTTPException(status_code=400, detail="Failed to create schedule entry")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.delete("/entry/{entry_id}", response_model=dict)
async def delete_schedule_entry_route(
    entry_id: int,
    current_user: User = Depends(get_current_user)
) -> dict:
    try:
        schedule_id = get_schedule_entry_schedule_id(entry_id)
        if schedule_id is None:
            raise HTTPException(status_code=404, detail="Schedule entry not found")
            
        club_id = get_schedule_club_id(schedule_id)
        if club_id is None:
            raise HTTPException(status_code=404, detail="Schedule not found")
            
        await require_club_access(club_id)(current_user)
        
        success = delete_schedule_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule entry not found")
            
        return {
            "success": True,
            "message": "Schedule entry deleted successfully",
            "action": "delete",
            "entry_id": entry_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))