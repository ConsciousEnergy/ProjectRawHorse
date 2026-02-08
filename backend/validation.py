"""
Input validation and sanitization for API query parameters.
- Limit search string length to 200 chars.
- Strip SQL-injection style patterns from search inputs.
- Validate date format (YYYY-MM-DD), entity_id format, amount ranges.
"""
import re
from datetime import datetime
from typing import Optional, Tuple

# Limits
MAX_SEARCH_LENGTH = 200
MAX_ENTITY_ID_LENGTH = 200
AMOUNT_MIN = 0
AMOUNT_MAX = 1e15  # 1 quadrillion USD
DATE_FMT = "%Y-%m-%d"

# Entity ID: alphanumeric, underscore, hyphen, period
ENTITY_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")


def sanitize_search(value: Optional[str]) -> Optional[str]:
    """Sanitize search string: strip, limit length, remove dangerous patterns."""
    if value is None:
        return None
    s = (value or "").strip()
    if not s:
        return None
    # Remove null bytes and control characters
    s = "".join(c for c in s if ord(c) >= 32 and ord(c) != 127)
    # Strip common SQL-like fragments that might be used in raw concatenation
    for pat in ("--", ";\s*", "/\*", "\*/", "'\s*or\s*'", "\"\s*or\s*\""):
        s = re.sub(pat, "", s, flags=re.IGNORECASE)
    s = s.strip()
    return s[:MAX_SEARCH_LENGTH] if s else None


def validate_entity_id(entity_id: str) -> Tuple[bool, Optional[str]]:
    """Validate entity_id format. Returns (ok, error_message)."""
    if not entity_id or len(entity_id) > MAX_ENTITY_ID_LENGTH:
        return False, "Invalid entity_id length"
    if not ENTITY_ID_PATTERN.match(entity_id):
        return False, "Invalid entity_id format"
    return True, None


def validate_date(date_str: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Validate date string YYYY-MM-DD. Returns (ok, error_message)."""
    if not date_str:
        return True, None
    try:
        datetime.strptime(date_str.strip(), DATE_FMT).date()
        return True, None
    except ValueError:
        return False, f"Invalid date format; use {DATE_FMT}"


def validate_amount(value: Optional[float]) -> Tuple[bool, Optional[str]]:
    """Validate amount in range [AMOUNT_MIN, AMOUNT_MAX]. Returns (ok, error_message)."""
    if value is None:
        return True, None
    if not isinstance(value, (int, float)):
        return False, "Amount must be a number"
    if value < AMOUNT_MIN or value > AMOUNT_MAX:
        return False, f"Amount must be between {AMOUNT_MIN} and {AMOUNT_MAX}"
    return True, None
