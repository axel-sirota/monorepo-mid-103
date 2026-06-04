"""
Shared validators — extracted from:
  - apps/user-service/app/services/user_service.py
  - apps/notification-service/internal/service/email_utils.go (Go equivalent)

Lab 3 extraction target. Import this in user-service to replace the local copy.
"""
import re
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email address format. RFC 5322 simplified."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_date(dt: datetime, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
    """Format a datetime to ISO 8601 string."""
    return dt.strftime(fmt)
