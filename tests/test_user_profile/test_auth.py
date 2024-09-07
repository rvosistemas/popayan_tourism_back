import pytest
import jwt
from unittest.mock import MagicMock, patch
from user_profile.models import User
from user_profile.auth import JWTAuth
from django.conf import settings


@pytest.mark.asyncio
async def test_jwt_authenticate_success():
    token = jwt.encode({"user_id": 1}, settings.SECRET_KEY, algorithm="HS256")
    user_mock = MagicMock()

    with patch('user_profile.models.User.objects.get', return_value=user_mock) as mock_get:
        auth = JWTAuth()
        user = await auth.authenticate(request=None, token=token)  # Asegúrate de usar await aquí

        mock_get.assert_called_once_with(id=1)
        assert user == user_mock


@pytest.mark.asyncio
async def test_jwt_authenticate_expired_token():
    expired_token = jwt.encode({"user_id": 1}, settings.SECRET_KEY, algorithm="HS256")

    with patch('user_profile.auth.jwt.decode', side_effect=jwt.ExpiredSignatureError):  # Asegúrate de usar el path correcto
        auth = JWTAuth()
        user = await auth.authenticate(request=None, token=expired_token)  # Asegúrate de usar await aquí

        assert user is None


@pytest.mark.asyncio
async def test_jwt_authenticate_invalid_token():
    invalid_token = "invalid.token"

    with patch('user_profile.auth.jwt.decode', side_effect=jwt.InvalidTokenError):  # Asegúrate de usar el path correcto
        auth = JWTAuth()
        user = await auth.authenticate(request=None, token=invalid_token)  # Asegúrate de usar await aquí

        assert user is None


@pytest.mark.asyncio
async def test_jwt_authenticate_user_not_found():
    token = jwt.encode({"user_id": 999}, settings.SECRET_KEY, algorithm="HS256")

    with patch('user_profile.models.User.objects.get', side_effect=User.DoesNotExist):
        auth = JWTAuth()
        user = await auth.authenticate(request=None, token=token)  # Asegúrate de usar await aquí

        assert user is None


@pytest.mark.asyncio
async def test_jwt_authenticate_general_exception():
    token = jwt.encode({"user_id": 1}, settings.SECRET_KEY, algorithm="HS256")

    with patch('user_profile.models.User.objects.get', side_effect=Exception("Unexpected error")):
        auth = JWTAuth()
        user = await auth.authenticate(request=None, token=token)  # Asegúrate de usar await aquí

        assert user is None
