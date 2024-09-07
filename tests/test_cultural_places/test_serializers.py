import pytest
from cultural_places.serializers import CulturalPlaceSerializer


@pytest.mark.django_db
def test_cultural_place_serializer_validate():
    valid_data = {
        'name': 'Museo de Historia Natural',
        'description': 'Un museo con colecciones de historia natural.',
        'address': 'Av. Central 123, Ciudad',
        'opening_hours': {
            "monday": "09:00-17:00",
            "tuesday": "09:00-17:00",
            "wednesday": "09:00-17:00",
            "thursday": "09:00-17:00",
            "friday": "09:00-17:00",
            "saturday": "10:00-18:00",
            "sunday": "closed"
        },
        'image': None
    }

    serializer = CulturalPlaceSerializer(data=valid_data)

    assert serializer.is_valid()

    validated_data = serializer.validate(serializer.validated_data)

    assert validated_data == serializer.validated_data
