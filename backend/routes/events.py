from fastapi import APIRouter, HTTPException, Depends
from database.events import get_club_events
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
