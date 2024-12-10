from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import users
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from models.users import User

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY', SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Generate a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def create_tokens(user_data: dict) -> Token:
    """Create both access and refresh tokens."""
    return Token(
        access_token=create_access_token(user_data),
        refresh_token=create_refresh_token(user_data)
    )

def verify_token(token: str, secret_key: str = SECRET_KEY) -> Tuple[bool, dict]:
    """Verify a token and return its payload."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return True, payload
    except ExpiredSignatureError:
        return False, {"error": "Token has expired"}
    except JWTError:
        return False, {"error": "Invalid token"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Retrieve the current user based on the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    is_valid, payload = verify_token(token)
    if not is_valid:
        raise credentials_exception

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user_data = users.get_user_by_username(username)
    if user_data is None:
        raise credentials_exception

    # Convert RealDictRow to User model
    return User(
        user_id=user_data["user_id"],
        username=user_data["username"],
        email=user_data["email"],
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        role=user_data.get("role", "member")
    )

async def refresh_access_token(refresh_token: str) -> Token:
    """Create new access token using refresh token."""
    is_valid, payload = verify_token(refresh_token, REFRESH_SECRET_KEY)
    if not is_valid or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    user = users.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_tokens({"sub": username})
