'''
Filename: teams.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from database.teams import create_team, get_teams, delete_team, update_team
from auth import get_current_user
from models.users import User

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    include_in_schema=True,
    redirect_slashes=False
)

class TeamBase(BaseModel):
    name: str
    year: str = Field(..., pattern=r'^U([4-9]|1[0-9]|2[0-4])$')
    club_id: int
    gender: str = Field(..., pattern='^(boys|girls)$')
    is_academy: bool
    minimum_field_size: int = Field(..., ge=125, le=1000)
    preferred_field_size: Optional[int] = Field(None, ge=125, le=1000)
    level: int = Field(..., ge=1, le=5)
    is_active: bool = True

    @model_validator(mode='after')
    def validate_field_sizes(self):
        valid_sizes = [125, 250, 500, 1000]
        if self.minimum_field_size not in valid_sizes:
            raise ValueError('Field size must be one of: 125, 250, 500, 1000')
        if self.preferred_field_size is not None and self.preferred_field_size not in valid_sizes:
            raise ValueError('Preferred field size must be one of: 125, 250, 500, 1000')
        return self

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    team_id: int

    class Config:
        from_attributes = True

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[str] = Field(None, pattern=r'^U([4-9]|1[0-9]|2[0-4])$')
    club_id: Optional[int] = None
    gender: Optional[str] = Field(None, pattern='^(boys|girls)$')
    is_academy: Optional[bool] = None
    minimum_field_size: Optional[int] = Field(None, ge=125, le=1000)
    preferred_field_size: Optional[int] = Field(None, ge=125, le=1000)
    level: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None

    @model_validator(mode='after')
    def validate_field_sizes(self):
        valid_sizes = [125, 250, 500, 1000]
        if self.minimum_field_size is not None and self.minimum_field_size not in valid_sizes:
            raise ValueError('Field size must be one of: 125, 250, 500, 1000')
        if self.preferred_field_size is not None and self.preferred_field_size not in valid_sizes:
            raise ValueError('Preferred field size must be one of: 125, 250, 500, 1000')
        return self

@router.post("", response_model=Team) 
async def create_team_route(team: TeamCreate, current_user: User = Depends(get_current_user)):
    try:
        return create_team(team.dict())
    except Exception as e:
        if 'unique_team_name_per_club' in str(e):
            raise HTTPException(status_code=400, detail="Team name already exists for this club")
        if 'teams_club_id_fkey' in str(e):
            raise HTTPException(status_code=400, detail="Invalid club_id")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Team])
async def get_teams_route(club_id: int, include_inactive: bool = False, current_user: User = Depends(get_current_user)):
    return get_teams(club_id, include_inactive)

@router.delete("/{team_id}")
async def delete_team_route(team_id: int, current_user: User = Depends(get_current_user)):
    result = delete_team(team_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Team not found")
    
    message = "Team successfully deleted" if result["action"] == "hard_deleted" else "Team deactivated due to existing schedule references"
    return {"message": message, "action": result["action"]}

@router.patch("/{team_id}", response_model=Team)
async def update_team_route(
    team_id: int, 
    team_update: TeamUpdate, 
    current_user: User = Depends(get_current_user)
):
    try:
        updated_team = update_team(team_id, team_update.model_dump(exclude_unset=True))
        if not updated_team:
            raise HTTPException(status_code=404, detail="Team not found")
        return updated_team
    except Exception as e:
        if 'unique_team_name_per_club' in str(e):
            raise HTTPException(status_code=400, detail="Team name already exists for this club")
        if 'teams_club_id_fkey' in str(e):
            raise HTTPException(status_code=400, detail="Invalid club_id")
        raise HTTPException(status_code=400, detail=str(e))