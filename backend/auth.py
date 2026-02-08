"""
Authentication module for Project RawHorse
JWT-based authentication for write operations

Read operations are public, write operations require authentication.
Auth is OFF by default; set AUTH_ENABLED=true in .env for multi-user deployments.
"""
import os
import re
import secrets
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

# Try to import bcrypt for password hashing
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    bcrypt = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Account lockout: track failed attempts per username
# Format: {username: (attempt_count, lockout_until_datetime)}
_failed_attempts: dict = {}
LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES = 15


def _ensure_secret_key() -> str:
    """Return SECRET_KEY from env, or auto-generate and write to .env if not set."""
    key = os.environ.get("SECRET_KEY", "").strip()
    if key and key != "dev-secret-key-change-in-production":
        return key
    # Auto-generate and persist
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    env_path = os.path.join(project_root, ".env")
    new_key = secrets.token_urlsafe(32)
    try:
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                content = f.read()
            if "SECRET_KEY=" in content:
                # Replace existing SECRET_KEY line
                content = re.sub(r"SECRET_KEY=.*", f"SECRET_KEY={new_key}", content)
            else:
                content = content.rstrip() + f"\nSECRET_KEY={new_key}\n"
        else:
            content = f"# Project RawHorse - auto-generated\nSECRET_KEY={new_key}\nAUTH_ENABLED=false\n"
        with open(env_path, "w") as f:
            f.write(content)
        os.environ["SECRET_KEY"] = new_key
        logger.info("SECRET_KEY auto-generated and written to .env")
        return new_key
    except Exception as e:
        logger.warning(f"Could not write .env for SECRET_KEY: {e}. Using in-memory key.")
        os.environ["SECRET_KEY"] = new_key
        return new_key


# Configuration
class AuthConfig:
    """Authentication configuration from environment"""
    SECRET_KEY: str = None  # Set in __init__
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AUTH_ENABLED: bool = os.environ.get('AUTH_ENABLED', 'false').lower() == 'true'

    def __init__(self):
        self.SECRET_KEY = _ensure_secret_key()


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


# Password complexity requirements (when auth is enabled and validating new passwords)
PASSWORD_MIN_LENGTH = 10
PASSWORD_REQUIRE_UPPER = True
PASSWORD_REQUIRE_LOWER = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:',.<>?/"


def validate_password_complexity(password: str) -> tuple[bool, Optional[str]]:
    """Validate password meets complexity requirements. Returns (ok, error_message)."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
    if PASSWORD_REQUIRE_UPPER and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if PASSWORD_REQUIRE_LOWER and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r"[%s]" % re.escape(PASSWORD_SPECIAL_CHARS), password):
        return False, "Password must contain at least one special character"
    return True, None


def hash_password(plain_password: str) -> str:
    """Hash password with bcrypt. Falls back to plaintext only if bcrypt not installed (demo)."""
    if BCRYPT_AVAILABLE:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return plain_password  # Fallback for installs without bcrypt (not recommended)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash, or plaintext if bcrypt unavailable."""
    if not plain_password:
        return False
    if BCRYPT_AVAILABLE:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password,
            )
        except Exception:
            return False
    return plain_password == hashed_password  # Fallback when bcrypt not installed


# Demo user: password is "admin" hashed with bcrypt (or plain "admin" if no bcrypt)
# In production, replace with database-backed user store
def _demo_password_hash() -> str:
    if BCRYPT_AVAILABLE:
        return bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode("utf-8")
    return "admin"


DEMO_USERS = {
    "admin": {
        "username": "admin",
        "password_hash": None,  # Set lazily with bcrypt hash
        "email": "admin@example.com",
        "is_admin": True,
        "scopes": ["read", "write", "admin"]
    }
}


def _get_demo_user(username: str) -> Optional[dict]:
    """Return demo user with password_hash initialized."""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    if user.get("password_hash") is None:
        user["password_hash"] = _demo_password_hash()
    return user


def _check_lockout(username: str) -> Optional[str]:
    """Return error message if user is locked out, else None."""
    now = datetime.utcnow()
    if username not in _failed_attempts:
        return None
    count, lockout_until = _failed_attempts[username]
    if lockout_until and now < lockout_until:
        remaining = (lockout_until - now).seconds
        return f"Account temporarily locked. Try again in {remaining // 60} minutes."
    if lockout_until and now >= lockout_until:
        del _failed_attempts[username]
    return None


def _record_failed_login(username: str) -> None:
    """Record a failed login; lock out after LOCKOUT_THRESHOLD attempts."""
    now = datetime.utcnow()
    if username not in _failed_attempts:
        _failed_attempts[username] = (1, None)
        return
    count, lockout_until = _failed_attempts[username]
    if lockout_until and now < lockout_until:
        return
    if lockout_until and now >= lockout_until:
        count = 0
    count += 1
    if count >= LOCKOUT_THRESHOLD:
        _failed_attempts[username] = (count, now + timedelta(minutes=LOCKOUT_MINUTES))
        logger.warning(f"Account locked for {username} after {count} failed attempts")
    else:
        _failed_attempts[username] = (count, None)


def _record_successful_login(username: str) -> None:
    """Clear failed attempts on successful login."""
    if username in _failed_attempts:
        del _failed_attempts[username]


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password. Enforces lockout after 5 failed attempts."""
    if not username or not password:
        return None
    lockout_msg = _check_lockout(username)
    if lockout_msg:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=lockout_msg)
    user = _get_demo_user(username)
    if not user:
        _record_failed_login(username)
        return None
    if not verify_password(password, user["password_hash"]):
        _record_failed_login(username)
        return None
    _record_successful_login(username)
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
