"""
Authentication module for Project RawHorse
JWT-based authentication for write operations

Read operations are public, write operations require authentication.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Union
from functools import wraps

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Try to import PyJWT, provide fallback if not installed
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class AuthConfig:
    """Authentication configuration from environment"""
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AUTH_ENABLED: bool = os.environ.get('AUTH_ENABLED', 'false').lower() == 'true'


config = AuthConfig()


# Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list = []
    exp: Optional[datetime] = None


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    is_admin: bool = False


# Security
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if not JWT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication not available. Install PyJWT."
        )
    
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    if not JWT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication not available. Install PyJWT."
        )
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token"""
    if not JWT_AVAILABLE:
        return None
    
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        scopes: list = payload.get("scopes", [])
        exp = payload.get("exp")
        
        if username is None:
            return None
        
        return TokenData(
            username=username,
            scopes=scopes,
            exp=datetime.fromtimestamp(exp) if exp else None
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """Get current user from JWT token (optional - for public endpoints)"""
    if not config.AUTH_ENABLED:
        # Auth disabled - return None but don't fail
        return None
    
    if credentials is None:
        return None
    
    token_data = verify_token(credentials.credentials)
    return token_data


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """Require authentication for an endpoint"""
    if not config.AUTH_ENABLED:
        # Auth disabled - allow all
        return TokenData(username="anonymous", scopes=["write"])
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(credentials.credentials)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def require_admin(
    token_data: TokenData = Depends(require_auth)
) -> TokenData:
    """Require admin privileges for an endpoint"""
    if not config.AUTH_ENABLED:
        return TokenData(username="anonymous", scopes=["admin"])
    
    if "admin" not in token_data.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return token_data


def require_scope(required_scope: str):
    """Dependency factory to require a specific scope"""
    async def scope_checker(token_data: TokenData = Depends(require_auth)) -> TokenData:
        if not config.AUTH_ENABLED:
            return TokenData(username="anonymous", scopes=[required_scope])
        
        if required_scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope '{required_scope}' required"
            )
        return token_data
    
    return scope_checker


# Simple user storage (for demo - replace with database in production)
# In production, users should be stored in the database with hashed passwords
DEMO_USERS = {
    "admin": {
        "username": "admin",
        "password_hash": "change-this-hash",  # In production: use bcrypt
        "email": "admin@example.com",
        "is_admin": True,
        "scopes": ["read", "write", "admin"]
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (simplified - use bcrypt in production)"""
    # In production, use: bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return plain_password == hashed_password  # DEMO ONLY


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password"""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


# Utility functions
def get_auth_status() -> dict:
    """Get current authentication status"""
    return {
        "auth_enabled": config.AUTH_ENABLED,
        "jwt_available": JWT_AVAILABLE,
        "algorithm": config.ALGORITHM,
        "token_expiry_minutes": config.ACCESS_TOKEN_EXPIRE_MINUTES
    }
