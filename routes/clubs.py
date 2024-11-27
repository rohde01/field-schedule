'''
Filename: clubs.py in routes folder
'''
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import clubs

router = APIRouter(prefix="/clubs", tags=["clubs"])

class ClubCreate(BaseModel):
    name: str

class UserClubCreate(BaseModel):
    user_id: int
    is_primary: bool = False

@router.post("/")
async def create_club(club: ClubCreate):
    return clubs.create_club(club.dict())

@router.get("/{club_id}")
async def get_club(club_id: int):
    club = clubs.get_club(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club

@router.post("/{club_id}/users")
async def add_user_to_club(club_id: int, user_club: UserClubCreate):
    return clubs.add_user_to_club(user_club.user_id, club_id, user_club.is_primary)
