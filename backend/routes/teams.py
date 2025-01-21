'''
Filename: teams.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from database.teams import create_team, get_teams, delete_team, update_team, get_teams_by_ids
from dependencies.auth import get_current_user
from dependencies.permissions import require_club_access
from backend.models.user import User
from backend.models.team import Team

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    include_in_schema=True,
    redirect_slashes=False
)

@router.post("", response_model=Team)
async def create_team_route(
    team: Team,
    current_user: User = Depends(get_current_user)
):
    # Check club access before creating team
    await require_club_access(team.club_id)(current_user)
    try:
        return create_team(team.model_dump())
    except Exception as e:
        if 'unique_team_name_per_club' in str(e):
            raise HTTPException(status_code=400, detail="Team name already exists for this club")
        if 'teams_club_id_fkey' in str(e):
            raise HTTPException(status_code=400, detail="Invalid club_id")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Team])
async def get_teams_route(
    club_id: int,
    include_inactive: bool = True,
    current_user: User = Depends(get_current_user)
):
    await require_club_access(club_id)(current_user)
    return get_teams(club_id, include_inactive)

@router.delete("/{team_id}")
async def delete_team_route(team_id: int, current_user: User = Depends(get_current_user)):
    teams = get_teams_by_ids([team_id])
    if not teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    await require_club_access(teams[0].club_id)(current_user)
    
    result = delete_team(team_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Team not found")
    
    message = "Team successfully deleted" if result["action"] == "hard_deleted" else "Team deactivated due to existing schedule references"
    return {"message": message}

@router.patch("/{team_id}", response_model=Team)
async def update_team_route(
    team_id: int, 
    team_update: Team, 
    current_user: User = Depends(get_current_user)
):
    teams = get_teams_by_ids([team_id])
    if not teams:
        raise HTTPException(status_code=404, detail="Team not found")
    
    await require_club_access(teams[0].club_id)(current_user)
    
    try:
        result = update_team(team_id, team_update.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Team not found")
        return result
    except Exception as e:
        if 'unique_team_name_per_club' in str(e):
            raise HTTPException(status_code=400, detail="Team name already exists for this club")
        if 'teams_club_id_fkey' in str(e):
            raise HTTPException(status_code=400, detail="Invalid club_id")
        raise HTTPException(status_code=400, detail=str(e))