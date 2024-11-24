from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from database.teams import create_team, get_teams, delete_team

router = APIRouter(
    prefix="/teams",
    tags=["teams"]
)

class TeamBase(BaseModel):
    name: str
    year: Optional[str] = None
    club_id: int
    is_active: bool = True

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    team_id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=Team)
async def create_team_route(team: TeamCreate):
    try:
        return create_team(team.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Team])
async def get_teams_route(club_id: int, include_inactive: bool = False):
    return get_teams(club_id, include_inactive)

@router.delete("/{team_id}")
async def delete_team_route(team_id: int, hard_delete: bool = False):
    success = delete_team(team_id, hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted successfully"}