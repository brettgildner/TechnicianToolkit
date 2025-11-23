from datetime import datetime
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

"""
This page provides a collection of utility functions used throughout the application to safely 
clean, validate, and format user input. It includes helpers for converting values into safe 
strings and numbers, parsing and formatting dates and times, combining date/time fields, and 
computing duration differences. Additional validation tools ensure fields aren’t empty and that 
date or time strings match expected formats. The module also includes a route-normalization helper 
that standardizes user-entered paths, and a style_button function used across UI pages to apply 
consistent button styling and cursor behavior. Together, these utilities form the shared foundation 
for reliable data handling and uniform UI appearance.

core.utils.py index:
- def safe_str(): Converts any value into a string
- def safe_int(): Converts a value to an integer
- def safe_float(): Converts a value to a float
- def parse_date(): Parses a date string using the given format
- def format_date(): Formats a datetime object into a string
- def parse_time(): Parses a 12-hour time string
- def combine_datetime(): Combines a date string and time string into a datetime
- def diff_hours_minutes(): Computes the time difference between two datetimes
- def is_empty(): Returns True if a value is empty
- def non_empty(): Validates that a field contains text
- def validate_date_string(): Validates that a date string matches the expected format
- def validate_time_string(): Validates user-entered time strings in AM/PM format
- def normalize_route(): Normalizes a route string
- def style_button(): Applies the theme to the page
"""

# These helpers clean unpredictable user input and standardize values across the app.
def safe_str(value) -> str:
    # Converts any value into a clean, trimmed string, returning an empty string for None.
    if value is None:
        return ""
    return str(value).strip()

# These functions safely convert values to numbers and prevent crashes from invalid input.
def safe_int(value, default=0) -> int:
    # Converts a value to an integer or returns the default when parsing fails.
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0) -> float:
    # Converts a value to a float or returns the default when parsing fails.
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# These helpers provide consistent, safe parsing and formatting for date and time values.
def parse_date(date_str: str, fmt="%Y-%m-%d") -> datetime | None:
    # Parses a date string using the given format, returning None when parsing fails.
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        return None


def format_date(dt: datetime | None, fmt="%Y-%m-%d") -> str:
    # Formats a datetime object into a string or returns an empty string when value is None.
    if not dt:
        return ""
    return dt.strftime(fmt)


def parse_time(time_str: str) -> datetime | None:
    # Parses a 12-hour time string like '3:45 PM' and returns None for invalid formats.
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str.strip(), "%I:%M %p")
    except ValueError:
        return None

# These utilities merge date and time fields and compute safe duration differences.
def combine_datetime(date_str: str, time_str: str) -> datetime | None:
    # Combines a date string and time string into a datetime, returning None if either is invalid.
    d = parse_date(date_str)
    t = parse_time(time_str)
    if not d or not t:
        return None
    return datetime(d.year, d.month, d.day,t.hour, t.minute)


def diff_hours_minutes(dt_start: datetime, dt_end: datetime) -> tuple[int, int]:
    # Computes the time difference between two datetimes, returning hours and minutes safely.
    if not dt_start or not dt_end:
        return (0, 0)
    diff = dt_end - dt_start
    minutes = max(0, int(diff.total_seconds() // 60))
    return divmod(minutes, 60)

# Helper functions for lightweight and exception-free input validation.
def is_empty(value) -> bool:
    # Returns True if a value is empty after trimming.
    return safe_str(value) == ""

def non_empty(value: str, field_name="Field") -> tuple[bool, str]:
    # Validates that a field contains text, returning (success, message).
    if is_empty(value):
        return False, f"{field_name} is required."
    return True, ""

def validate_date_string(date_str: str) -> tuple[bool, str]:
    # Validates that a date string matches the expected format.
    if not parse_date(date_str):
        return False, f"Invalid date: {date_str}"
    return True, ""

def validate_time_string(time_str: str) -> tuple[bool, str]:
    # Validates user-entered time strings in AM/PM format.
    if not parse_time(time_str):
        return False, f"Invalid time: {time_str}"
    return True, ""

# Normalizes user-typed route strings into a consistent "start, end" tuple.
def normalize_route(route: str) -> tuple[str, str] | None:
    # Normalizes a route string by cleaning arrow variations and splitting into (start, end).
    if not route:
        return None
    # normalize messy arrows/spaces
    clean = re.sub(r'\s*->\s*', '→', route)
    clean = re.sub(r'\s*→\s*', '→', clean)

    if "→" not in clean:
        return None
    start, end = clean.split("→", 1)
    return safe_str(start), safe_str(end)

# Applies the theme to the page, used in equipment info, expense report, inventory,
# mileage, parts, and the service activity page.
def style_button(btn, color: str):
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: #ffffff;
            border-radius: 6px;
            padding: 6px 10px;
            font: bold 14px 'Segoe UI';
        }}
        QPushButton:hover {{
            background-color: #333333;
            color: #00ff99;
        }}
    """)