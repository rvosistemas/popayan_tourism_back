import re
from django.core.exceptions import ValidationError
from datetime import datetime

# Regex pattern to match hours in the format "HH:MM-HH:MM"
HOURS_PATTERN = re.compile(r'^\d{2}:\d{2}-\d{2}:\d{2}$')
VALID_DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


def is_valid_day(day):
    """Check if the day is valid."""
    if day not in VALID_DAYS:
        raise ValidationError(f"Not a valid day: {day}. Valid days are: {', '.join(VALID_DAYS)}.")


def is_valid_hours_format(hours, day):
    """Check if the hours follow the correct format 'HH:MM-HH:MM'."""
    if not HOURS_PATTERN.match(hours):
        raise ValidationError(f"Hours must follow the format 'HH:MM-HH:MM' for {day}: {hours}.")


def is_valid_hours_range(hours):
    """Check if the opening hour is less than the closing hour."""
    opening_time_str, closing_time_str = hours.split('-')
    opening_time = datetime.strptime(opening_time_str, '%H:%M')
    closing_time = datetime.strptime(closing_time_str, '%H:%M')

    if opening_time >= closing_time:
        raise ValidationError("The opening hour must be less than the closing hour.")


def validate_opening_hours(value):
    """
    Validator for the 'opening_hours' field in the 'CulturalPlace' model.
    Ensures that the hours follow the format "HH:MM-HH:MM" and that the days are valid.
    Verifies that the opening hour is less than the closing hour.
    """
    if not isinstance(value, dict):
        raise ValidationError("The opening_hours field must be a JSON object.")

    for day, hours in value.items():
        is_valid_day(day)

        if hours != "closed":
            is_valid_hours_format(hours, day)
            is_valid_hours_range(hours)

    return value
