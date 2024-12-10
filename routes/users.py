'''
Filename: users.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from database import users
from dependencies.auth import create_access_token, get_current_user
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from database import clubs
from models.users import User

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
    existing = users.check_existing_credentials(user.username, user.email)
    if existing:
        if existing['username'] == user.username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    created_user_data = users.create_user(user.dict())
    return User(
        user_id=created_user_data["user_id"],
        username=created_user_data["username"],
        email=created_user_data["email"],
        first_name=created_user_data.get("first_name"),
        last_name=created_user_data.get("last_name"),
        role=created_user_data.get("role", "member")
    )

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = users.authenticate_user(form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user_data["username"]})
    primary_club_id = users.get_user_primary_club(user_data["user_id"])
    has_facilities = clubs.club_has_facilities(primary_club_id) if primary_club_id else False
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            role=user_data.get("role", "member")
        ),
        "primary_club_id": primary_club_id,
        "has_facilities": has_facilities
    }

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    primary_club_id = users.get_user_primary_club(current_user.user_id)
    return {**current_user.dict(), "primary_club_id": primary_club_id}

@router.get("/{user_id}")
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    user_data = users.get_user(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        user_id=user_data["user_id"],
        username=user_data["username"],
        email=user_data["email"],
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        role=user_data.get("role", "member")
    )

@router.put("/{user_id}")
async def update_user(user_id: int, user: UserUpdate, current_user: User = Depends(get_current_user)):
    updated_user_data = users.update_user(user_id, user.dict(exclude_unset=True))
    if not updated_user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        user_id=updated_user_data["user_id"],
        username=updated_user_data["username"],
        email=updated_user_data["email"],
        first_name=updated_user_data.get("first_name"),
        last_name=updated_user_data.get("last_name"),
        role=updated_user_data.get("role", "member")
    )
