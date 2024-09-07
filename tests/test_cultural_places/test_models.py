import pytest
from unittest.mock import Mock
from cultural_places.models import CulturalPlace, UserPlacePreference
from django.contrib.auth import get_user_model


@pytest.fixture
def mock_cultural_place():
    place = CulturalPlace(
        name="Museo de Historia Natural",
        description="Un museo que alberga exposiciones de historia natural y paleontología.",
        address="Av. Central 45, Barrio Centro",
        opening_hours={
            "monday": "09:00-17:00",
            "tuesday": "09:00-17:00",
            "wednesday": "09:00-17:00",
            "thursday": "09:00-17:00",
            "friday": "09:00-17:00",
            "saturday": "10:00-18:00",
            "sunday": "closed"
        },
        image=None
    )
    return place


@pytest.fixture
def mock_user():
    user_model = get_user_model()
    user = Mock(spec=user_model)
    user.username = "testuser"
    user._state = Mock()
    return user


@pytest.fixture
def mock_user_place_preference(mock_cultural_place, mock_user):
    user_place_preference = UserPlacePreference(
        user=mock_user,
        place=mock_cultural_place,
        rating=5
    )
    return user_place_preference


def test_cultural_place_str(mock_cultural_place):
    assert str(mock_cultural_place) == "Museo de Historia Natural"


def test_user_place_preference_str(mock_user_place_preference):
    expected_str = f"user: {mock_user_place_preference.user.username}, place: {mock_user_place_preference.place.name}, rating: {mock_user_place_preference.rating}"
    assert str(mock_user_place_preference) == expected_str
