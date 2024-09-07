from unittest.mock import MagicMock
from cultural_places.pydantic_serializers import CulturalPlaceSchema


def test_from_orm_with_image():
    mock_obj = MagicMock()
    mock_obj.name = "Museo de Arte Moderno"
    mock_obj.description = "Un museo con colecciones de arte moderno."
    mock_obj.address = "Calle 123, Ciudad"
    mock_obj.opening_hours = {
        "monday": "09:00-17:00",
        "tuesday": "09:00-17:00",
        "wednesday": "09:00-17:00",
        "thursday": "09:00-17:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-18:00",
        "sunday": "closed"
    }

    mock_image = MagicMock()
    mock_image.url = "http://example.com/image.jpg"
    mock_obj.image = mock_image

    schema = CulturalPlaceSchema.from_orm(mock_obj)

    assert schema.image == "http://example.com/image.jpg"
