"""Utility helpers for the Task Manager API."""
from datetime import datetime
import re


def format_date(date_obj):
    """Format a datetime object to string."""
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    """Calculate a percentage safely handling zero division."""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    """Validate an email address format."""
    return bool(re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email))


def parse_date(date_string):
    """Parse a date string trying multiple formats."""
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None
