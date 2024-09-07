import pytest
from django.core.exceptions import ValidationError
from datetime import datetime
from cultural_places.validators import (
    is_valid_day,
    is_valid_hours_format,
    is_valid_hours_range,
    validate_opening_hours
)


def test_is_valid_day_valid():
    """Prueba con un día válido."""
    try:
        is_valid_day('monday')
    except ValidationError:
        pytest.fail("is_valid_day() levantó una excepción inesperada con un día válido.")


def test_is_valid_day_invalid():
    """Prueba con un día inválido."""
    with pytest.raises(ValidationError,
                       match=r"Not a valid day: holiday\. Valid days are: (monday|tuesday|wednesday|thursday|friday|saturday|sunday)(, (monday|tuesday|wednesday|thursday|friday|saturday|sunday))*\."):
        is_valid_day('holiday')


def test_is_valid_hours_format_valid():
    """Prueba con un formato de horas válido."""
    try:
        is_valid_hours_format('09:00-17:00', 'monday')
    except ValidationError:
        pytest.fail("is_valid_hours_format() levantó una excepción inesperada con un formato válido.")


def test_is_valid_hours_format_invalid():
    """Prueba con un formato de horas inválido."""
    with pytest.raises(ValidationError, match="Hours must follow the format 'HH:MM-HH:MM' for monday: 0900-1700."):
        is_valid_hours_format('0900-1700', 'monday')


def test_is_valid_hours_range_valid():
    """Prueba con un rango de horas válido."""
    try:
        is_valid_hours_range('09:00-17:00')
    except ValidationError:
        pytest.fail("is_valid_hours_range() levantó una excepción inesperada con un rango válido.")


def test_is_valid_hours_range_invalid():
    """Prueba con un rango de horas inválido."""
    with pytest.raises(ValidationError, match="The opening hour must be less than the closing hour."):
        is_valid_hours_range('17:00-09:00')


def test_validate_opening_hours_valid():
    """Prueba con un objeto de horas de apertura válido."""
    valid_hours = {
        "monday": "09:00-17:00",
        "tuesday": "09:00-17:00",
        "wednesday": "09:00-17:00",
        "thursday": "09:00-17:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-18:00",
        "sunday": "closed"
    }
    try:
        validate_opening_hours(valid_hours)
    except ValidationError:
        pytest.fail("validate_opening_hours() levantó una excepción inesperada con un objeto válido.")


def test_validate_opening_hours_invalid_type():
    """Prueba con un tipo de datos inválido para el campo de horas de apertura."""
    with pytest.raises(ValidationError, match="The opening_hours field must be a JSON object."):
        validate_opening_hours("09:00-17:00")


def test_validate_opening_hours_invalid_day():
    """Prueba con un día inválido en el objeto de horas de apertura."""
    invalid_hours = {
        "holiday": "09:00-17:00",
        "monday": "09:00-17:00"
    }
    with pytest.raises(ValidationError,
                       match=r"Not a valid day: holiday\. Valid days are: (monday|tuesday|wednesday|thursday|friday|saturday|sunday)(, (monday|tuesday|wednesday|thursday|friday|saturday|sunday))*\."):
        validate_opening_hours(invalid_hours)


def test_validate_opening_hours_invalid_format():
    """Prueba con un formato de horas inválido en el objeto de horas de apertura."""
    invalid_hours = {
        "monday": "0900-1700"
    }
    with pytest.raises(ValidationError, match="Hours must follow the format 'HH:MM-HH:MM' for monday: 0900-1700."):
        validate_opening_hours(invalid_hours)


def test_validate_opening_hours_invalid_range():
    """Prueba con un rango de horas inválido en el objeto de horas de apertura."""
    invalid_hours = {
        "monday": "17:00-09:00"
    }
    with pytest.raises(ValidationError, match="The opening hour must be less than the closing hour."):
        validate_opening_hours(invalid_hours)
