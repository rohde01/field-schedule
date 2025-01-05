'''
Filename: users.py in routes folder
'''

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from database import users
from dependencies.auth import create_tokens, get_current_user, Token, OAuth2PasswordBearer, refresh_access_token
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from database import clubs
from models.users import User

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "member"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/")
async def create_user(user: UserCreate):
    existing = users.check_existing_credentials(user.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    created_user_data = users.create_user(user.dict())
    return User(
        user_id=created_user_data["user_id"],
        email=created_user_data["email"],
        first_name=created_user_data.get("first_name"),
        last_name=created_user_data.get("last_name"),
        role=created_user_data.get("role", "member")
    )

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = users.authenticate_user(form_data.username, form_data.password)  # form_data.username contains email
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    tokens = create_tokens({"sub": user_data["email"]})
    primary_club_id = users.get_user_primary_club(user_data["user_id"])
    has_facilities = clubs.club_has_facilities(primary_club_id) if primary_club_id else False
    
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": "bearer",
        "user": User(
            user_id=user_data["user_id"],
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

@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """Endpoint to refresh access token using refresh token."""
    try:
        tokens = await refresh_access_token(request.refresh_token)
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing the token"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Simple logout endpoint that returns success message. enhance this to invalidate tokens in the future"""
    return {"message": "Successfully logged out"}
