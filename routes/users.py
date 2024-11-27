'''
Filename: users.py in routes folder
'''

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import users

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "member"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None

@router.post("/")
async def create_user(user: UserCreate):
    return users.create_user(user.dict())

@router.get("/{user_id}")
async def get_user(user_id: int):
    user = users.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    updated_user = users.update_user(user_id, user.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
