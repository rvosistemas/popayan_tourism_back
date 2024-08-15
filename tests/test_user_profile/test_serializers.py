import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from rest_framework.exceptions import ValidationError
from user_profile.serializers import UserSerializer

TEST_USER = 'test_user'
TEST_EMAIL = 'test_user@example.com'
TEST_PASSWORD = 'password123'


@pytest.fixture
def user_data():
    return {
        'username': TEST_USER,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'date_of_birth': date(2000, 1, 1)
    }


@patch('user_profile.models.User.objects.filter')
def test_user_serializer_valid(mock_filter, user_data):
    mock_filter.return_value.exists.return_value = False
    serializer = UserSerializer(data=user_data)
    assert serializer.is_valid()
    assert serializer.validated_data == user_data


@patch('user_profile.models.User.objects.filter')
def test_user_serializer_age_validation(mock_filter):
    mock_filter.return_value.exists.return_value = False

    data = {
        'username': TEST_USER,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'date_of_birth': date(2015, 1, 1)  # User younger than 12
    }
    serializer = UserSerializer(data=data)
    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)
    assert 'date_of_birth' in exc_info.value.detail
    assert exc_info.value.detail['date_of_birth'][0] == 'You must be at least 12 years old'

    data['date_of_birth'] = date(1900, 1, 1)  # User older than 100
    serializer = UserSerializer(data=data)
    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)
    assert 'date_of_birth' in exc_info.value.detail
    assert exc_info.value.detail['date_of_birth'][0] == 'Age cannot be more than 100 years'


@patch('user_profile.models.User.objects.filter')
def test_user_serializer_username_exists(mock_filter, user_data):
    mock_filter.return_value.exists.return_value = True

    serializer = UserSerializer(data=user_data)

    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)

    assert 'username' in exc_info.value.detail
    assert exc_info.value.detail['username'][0] == 'A user with that username already exists.'



@patch('user_profile.models.User.objects.filter')
def test_user_serializer_email_exists(mock_filter, user_data):
    def mock_filter_side_effect(*args, **kwargs):
        if kwargs == {'username': 'newusername'}:
            return MagicMock(exists=MagicMock(return_value=False))
        elif kwargs == {'email': TEST_EMAIL}:
            return MagicMock(exists=MagicMock(return_value=True))
        return MagicMock(exists=MagicMock(return_value=False))

    mock_filter.side_effect = mock_filter_side_effect

    user_data['username'] = 'newusername'
    serializer = UserSerializer(data=user_data)
    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)
    assert 'email' in exc_info.value.detail
    assert exc_info.value.detail['email'][0] == 'Email already exists'


@patch('user_profile.models.User.objects.create_user')
@patch('user_profile.models.User.objects.filter')
def test_user_serializer_create(mock_filter, mock_create_user, user_data):
    mock_filter.return_value.exists.return_value = False
    serializer = UserSerializer(data=user_data)
    assert serializer.is_valid()
    serializer.save()
    mock_create_user.assert_called_once_with(**user_data)
