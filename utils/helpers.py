"""
Helper utility functions for common operations.
"""

import json
import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


def format_date(date_obj: Any, format_str: str = "%Y-%m-%d") -> str:
    """Format a date object to string."""
    if isinstance(date_obj, str):
        return date_obj
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    return str(date_obj)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_part = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if prefix:
        return f"{prefix}_{timestamp}_{unique_part}"
    return f"{timestamp}_{unique_part}"


def safe_json_load(data: str, default: Any = None) -> Any:
    """Safely load JSON data."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dump(data: Any, default: str = "{}") -> str:
    """Safely dump data to JSON."""
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        return default


def hash_string(text: str) -> str:
    """Create a hash of a string."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def extract_hashtags(text: str) -> list:
    """Extract hashtags from text."""
    import re
    return re.findall(r'#(\w+)', text)