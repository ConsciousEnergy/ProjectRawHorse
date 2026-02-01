"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_user,
    get_current_user,
    get_auth_status,
    Token,
    TokenData,
    config
)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login and get access + refresh tokens"""
    if not config.AUTH_ENABLED:
        # Auth disabled - return demo tokens
        return LoginResponse(
            access_token="auth-disabled",
            refresh_token="auth-disabled",
            expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={"username": "anonymous", "is_admin": True}
        )
    
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["username"]}
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "username": user["username"],
            "email": user.get("email"),
            "is_admin": user.get("is_admin", False)
        }
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest):
    """Refresh an access token using a refresh token"""
    if not config.AUTH_ENABLED:
        return Token(
            access_token="auth-disabled",
            expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    token_data = verify_token(request.refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": token_data.username, "scopes": token_data.scopes}
    )
    
    return Token(
        access_token=access_token,
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me")
async def get_current_user_info(
    current_user: Optional[TokenData] = Depends(get_current_user)
):
    """Get current user information"""
    if not config.AUTH_ENABLED:
        return {
            "authenticated": False,
            "auth_enabled": False,
            "user": None
        }
    
    if not current_user:
        return {
            "authenticated": False,
            "auth_enabled": True,
            "user": None
        }
    
    return {
        "authenticated": True,
        "auth_enabled": True,
        "user": {
            "username": current_user.username,
            "scopes": current_user.scopes,
            "expires": current_user.exp.isoformat() if current_user.exp else None
        }
    }


@router.get("/status")
async def get_authentication_status():
    """Get authentication system status"""
    return get_auth_status()
