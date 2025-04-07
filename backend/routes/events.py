from fastapi import APIRouter, HTTPException, Depends
from datetime import date, time
from typing import Optional
from pydantic import BaseModel
from database.events import (
    get_club_events,
    create_event_override,
    update_event_override,
    delete_event_override
)
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access
from models.user import User

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/{club_id}")
async def fetch_club_events(
    club_id: int,
    current_user: User = Depends(get_current_user)
):
    # Verify that the user has access to this club
    await require_club_access(club_id)(current_user)
    
    # Fetch events (with overrides applied) for the given club_id
    events = get_club_events(club_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="No events found for this club")
    
    return events


# Request models for event override CRUD operations

class EventOverrideCreate(BaseModel):
    active_schedule_id: int
    override_date: date
    new_start_time: time
    new_end_time: time
    new_team_id: Optional[int] = None
    new_field_id: Optional[int] = None
    # If provided, indicates the base schedule entry to override.
    # If omitted, this override represents a one-off event.
    schedule_entry_id: Optional[int] = None
    is_deleted: bool = False

class EventOverrideUpdate(BaseModel):
    new_start_time: Optional[time] = None
    new_end_time: Optional[time] = None
    new_team_id: Optional[int] = None
    new_field_id: Optional[int] = None
    override_date: Optional[date] = None
    is_deleted: Optional[bool] = None


@router.post("/override", response_model=dict)
async def create_override(
    override: EventOverrideCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        new_id = create_event_override(
            active_schedule_id=override.active_schedule_id,
            override_date=override.override_date,
            new_start_time=override.new_start_time,
            new_end_time=override.new_end_time,
            new_team_id=override.new_team_id,
            new_field_id=override.new_field_id,
            schedule_entry_id=override.schedule_entry_id,
            is_deleted=override.is_deleted
        )
        return {"override_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/override/{override_id}", response_model=dict)
async def update_override(
    override_id: int,
    changes: EventOverrideUpdate,
    current_user: User = Depends(get_current_user)
):
    # (Optional) Validate permissions for the override here.
    try:
        # Exclude unset fields so only provided fields are updated.
        update_data = changes.dict(exclude_unset=True)
        updated = update_event_override(override_id, update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Override not found or no changes applied")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/override/{override_id}", response_model=dict)
async def delete_override(
    override_id: int,
    current_user: User = Depends(get_current_user)
):
    # (Optional) Validate permissions for the override here.
    try:
        deleted = delete_event_override(override_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Override not found")
        return {"success": True, "message": "Override deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
