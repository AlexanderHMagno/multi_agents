"""
Authentication Module for FastAPI Campaign Generation API

This module provides JWT-based authentication, user management,
and security utilities for the campaign generation API.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# In-memory user storage (replace with database in production)
users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("admin123"),
        "full_name": "Administrator",
        "disabled": False,
        "role": "admin"
    },
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "hashed_password": pwd_context.hash("password123"),
        "full_name": "Test User",
        "disabled": False,
        "role": "user"
    }
}


class User(BaseModel):
    """User model"""
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    disabled: Optional[bool] = Field(False, description="Account disabled status")
    role: str = Field("user", description="User role")


class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    full_name: Optional[str] = Field(None, description="User's full name")
    role: str = Field("user", description="User role")


class Token(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    """Get user by username"""
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current admin user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def create_user(username: str, email: str, password: str, full_name: str = None, role: str = "user") -> User:
    """Create a new user"""
    if username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(password)
    user_dict = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "disabled": False,
        "role": role
    }
    
    users_db[username] = user_dict
    return User(**{k: v for k, v in user_dict.items() if k != "hashed_password"})


def list_users() -> list:
    """List all users (admin only)"""
    return [
        User(**{k: v for k, v in user.items() if k != "hashed_password"})
        for user in users_db.values()
    ]


def delete_user(username: str) -> bool:
    """Delete a user (admin only)"""
    if username in users_db:
        del users_db[username]
        return True
    return False


def update_user_role(username: str, new_role: str) -> bool:
    """Update user role (admin only)"""
    if username in users_db:
        users_db[username]["role"] = new_role
        return True
    return False


def disable_user(username: str) -> bool:
    """Disable a user (admin only)"""
    if username in users_db:
        users_db[username]["disabled"] = True
        return True
    return False


def enable_user(username: str) -> bool:
    """Enable a user (admin only)"""
    if username in users_db:
        users_db[username]["disabled"] = False
        return True
    return False 