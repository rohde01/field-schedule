'''
Filename: clubs.py in routes folder
'''
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import clubs
from dependencies.auth import get_current_user
from models.user import User, UserClubCreate

router = APIRouter(prefix="/clubs", tags=["clubs"])

class ClubCreate(BaseModel):
    name: str

@router.post("/")
async def create_club(club: ClubCreate, current_user: User = Depends(get_current_user)):
    new_club = clubs.create_club({"name": club.name})
    clubs.add_user_to_club(current_user.user_id, new_club["club_id"], True)
    return {"club_id": new_club["club_id"], "name": new_club["name"]}

@router.get("/{club_id}")
async def get_club(club_id: int, current_user: User = Depends(get_current_user)):
    club = clubs.get_club(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club

@router.post("/{club_id}/users")
async def add_user_to_club(club_id: int, user_club: UserClubCreate, current_user: User = Depends(get_current_user)):
    return clubs.add_user_to_club(user_club.user_id, club_id, user_club.is_primary)
