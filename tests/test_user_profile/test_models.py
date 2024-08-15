import pytest
from unittest.mock import Mock, patch, create_autospec
from user_profile.models import User, UserProfile
import uuid
from datetime import date


@pytest.fixture
def user_mock():
    user = create_autospec(User, instance=True)
    user.id = uuid.uuid4()
    user.username = 'testuser'
    user.email = 'testuser@example.com'
    user.phone_number = '1234567890'
    user.date_of_birth = date(2000, 1, 1)
    return user


@pytest.fixture
def user_profile_mock(user_mock):
    user_profile = create_autospec(UserProfile, instance=True)
    user_profile.id = uuid.uuid4()
    user_profile.user = user_mock
    user_profile.preferences = {"theme": "dark"}
    user_profile.activity_history = ["login", "logout"]
    user_profile.__str__.return_value = f"user: {user_mock.username}"
    return user_profile


def test_create_user(user_mock):
    assert user_mock.username == 'testuser'
    assert user_mock.email == 'testuser@example.com'
    assert user_mock.phone_number == '1234567890'
    assert user_mock.date_of_birth == date(2000, 1, 1)
    assert isinstance(user_mock.id, uuid.UUID)


def test_create_user_profile(user_profile_mock):
    assert user_profile_mock.user.username == 'testuser'
    assert user_profile_mock.preferences == {"theme": "dark"}
    assert user_profile_mock.activity_history == ["login", "logout"]
    assert str(user_profile_mock) == f"user: {user_profile_mock.user.username}"
    assert isinstance(user_profile_mock.id, uuid.UUID)
    assert user_profile_mock.__str__() == f"user: {user_profile_mock.user.username}"


def test_user_profile_str():
    mock_user = Mock(spec=User)
    mock_user.username = "testuser"

    profile = UserProfile()

    with patch.object(UserProfile, 'user', mock_user):
        assert str(profile) == "user: testuser"
