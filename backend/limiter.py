"""Shared rate limiter for FastAPI app (used by main.py and auth_router)."""
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)
    SLOWAPI_AVAILABLE = True
except ImportError:
    limiter = None
    SLOWAPI_AVAILABLE = False
