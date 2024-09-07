import json
import os
import httpx


from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.asgi import ASGIHandler
from django.test import RequestFactory
from django.http import JsonResponse, HttpResponse
from django.core.asgi import get_asgi_application
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from httpx import AsyncClient
from ninja.testing import TestClient
from rest_framework.exceptions import ValidationError

from user_profile.api import api, password_reset_confirm_get, password_reset_confirm_post
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from user_profile.models import User
from user_profile.pydantic_serializers import PasswordResetSchema

os.environ['NINJA_SKIP_REGISTRY'] = '1'
client = TestClient(api)





@pytest.mark.asyncio
async def test_login_api():
    async def mock_handle_login(username, password):
        return JsonResponse({'token': 'test_token'}, status=200)

    with patch('user_profile.auth_utils.handle_login', new=mock_handle_login):
        with patch('user_profile.auth_utils.authenticate_user') as mock_authenticate_user:
            mock_authenticate_user.return_value = MagicMock(id=1, username="test", email="test@example.com")

            with patch('user_profile.auth_utils.generate_token', return_value='test_token'):
                request_data = {'username': 'test', 'password': 'test'}

                app = get_asgi_application()

                async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
                    response = await client.post('/user_profile/api/login', json=request_data)

                assert response.status_code == 200
                assert 'token' in response.json()
                assert response.json()['token'] == 'test_token'


@pytest.mark.asyncio
async def test_register_api():
    def mock_is_valid(*args, **kwargs):
        return True

    def mock_save(*args, **kwargs):
        user_mock = MagicMock()
        user_mock.username = 'testuser'
        user_mock.email = 'test@example.com'
        user_mock.password = 'password123'
        user_mock.date_of_birth = '2000-01-01'
        return user_mock

    with patch('user_profile.serializers.UserSerializer.is_valid', new=mock_is_valid):
        with patch('user_profile.serializers.UserSerializer.save', new=mock_save):
            request_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'date_of_birth': '2000-01-01'
            }

            app = get_asgi_application()
            async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
                response = await async_client.post('/user_profile/api/register', json=request_data)

            assert response.status_code == 201
            assert response.json()['username'] == 'testuser'
            assert response.json()['email'] == 'test@example.com'


@pytest.mark.asyncio
async def test_register_api_error():
    def mock_is_valid(*args, **kwargs):
        return False

    def mock_save(*args, **kwargs):
        raise ValueError("Mock save exception")

    mock_serializer_errors = {
        'username': ['This field is required.'],
        'email': ['Enter a valid email address.']
    }

    def mock_errors(*args, **kwargs):
        return mock_serializer_errors

    with patch('user_profile.serializers.UserSerializer.is_valid', new=mock_is_valid):
        with patch('user_profile.serializers.UserSerializer.errors', new=mock_errors):
            with patch('user_profile.serializers.UserSerializer.save', new=mock_save):
                request_data = {
                    'username': '',
                    'email': 'invalid-email',
                    'password': 'password123',
                    'date_of_birth': '2000-01-01'
                }

                app = ASGIHandler()
                async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
                    response = await async_client.post('/user_profile/api/register', json=request_data)

                assert response.status_code == 422
                response_data = response.json()

                assert 'detail' in response_data

                details = response_data['detail']
                assert any(error['loc'] == ['body', 'payload', 'username'] for error in details)
                assert any(error['loc'] == ['body', 'payload', 'email'] for error in details)
                assert any(error['msg'] == 'String should have at least 1 character' for error in details)
                assert any(
                    error['msg'] == 'value is not a valid email address: An email address must have an @-sign.' for
                    error in details)


@pytest.mark.asyncio
async def test_request_reset_password_api_success():
    async def mock_aget(*args, **kwargs):
        return User(username="testuser", email="test@example.com")

    with patch('user_profile.models.User.objects.aget', new=mock_aget):
        with patch('user_profile.api.generate_password_reset_token', return_value=('uid', 'token')):
            with patch('user_profile.api.send_password_reset_email') as mock_send_email:
                request_data = {'email': 'test@example.com'}

                app = get_asgi_application()
                async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
                    response = await async_client.post(
                        '/user_profile/api/request-reset-password',
                        json=request_data
                    )

                assert response.status_code == 200
                assert mock_send_email.called


@pytest.mark.asyncio
async def test_request_reset_password_api_user_not_exist():
    async def mock_aget(*args, **kwargs):
        raise ObjectDoesNotExist("User does not exist")

    with patch('user_profile.models.User.objects.aget', new=mock_aget):
        request_data = {'email': 'nonexistent@example.com'}

        app = get_asgi_application()
        async with AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.post(
                '/user_profile/api/request-reset-password',
                json=request_data
            )

        assert response.status_code == 400
        response_data = response.json()
        assert response_data['error'] == "User does not exist"


@pytest.mark.asyncio
async def test_password_reset_confirm_get():
    factory = RequestFactory()
    request = factory.get(
        '/reset-password/mockuid/mocktoken/',
        HTTP_X_CSRFTOKEN='mockcsrf'
    )

    with patch('user_profile.api.render') as mock_render:
        mock_context = {
            'uidb64': 'mockuid',
            'token': 'mocktoken',
            'csrf_token': 'mockcsrf'
        }
        mock_render.return_value = HttpResponse('Mocked response content')

        response = await password_reset_confirm_get(request, 'mockuid', 'mocktoken')

        assert response.status_code == 200
        assert 'Mocked response content' in response.content.decode()


@pytest.mark.asyncio
async def test_password_reset_confirm_post():
    factory = RequestFactory()
    request = factory.post(
        '/reset-password/mockuid/mocktoken/',
        data=json.dumps({"new_password": "new_password123"}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN='mockcsrf'
    )

    mock_user = User(pk=1)
    mock_user.set_password('old_password')
    mock_user.save = AsyncMock()
    mock_user.save.return_value = None

    with patch('user_profile.api.User.objects.aget', return_value=mock_user), \
            patch('user_profile.api.default_token_generator.check_token', return_value=True), \
            patch('user_profile.api.JsonResponse') as mock_json_response:

        mock_json_response.return_value = JsonResponse({"message": "Password has been reset"}, status=200)

        payload = PasswordResetSchema(new_password='new_password123')

        try:
            response = await password_reset_confirm_post(request, 'mockuid', 'mocktoken', payload)
        except ValueError as e:
            response = JsonResponse({"error": str(e)}, status=400)

        assert response.status_code == 200
        assert response.content == b'{"message": "Password has been reset"}'


@pytest.mark.asyncio
async def test_password_reset_confirm_post():
    factory = RequestFactory()
    request = factory.post(
        '/reset-password/mockuid/mocktoken/',
        data=json.dumps({"new_password": "new_password123"}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN='mockcsrf'
    )

    mock_user = User(pk=1)
    mock_user.set_password = MagicMock()
    mock_user.save = MagicMock()

    with patch('user_profile.api.User.objects.aget', AsyncMock(return_value=mock_user)), \
            patch('user_profile.api.default_token_generator.check_token', return_value=True):
        uidb64 = urlsafe_base64_encode(force_bytes(str(mock_user.pk)))
        payload = PasswordResetSchema(new_password='new_password123')

        response = await password_reset_confirm_post(request, uidb64, 'mocktoken', payload)
        assert response.status_code == 200
        assert response.content == b'{"message": "Password has been reset"}'


from pydantic import ValidationError


@pytest.mark.asyncio
async def test_password_reset_confirm_post_no_password():
    factory = RequestFactory()
    request = factory.post(
        '/reset-password/mockuid/mocktoken/',
        data=json.dumps({"new_password": ""}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN='mockcsrf'
    )

    mock_user = User(pk=1)
    mock_user.set_password = MagicMock()
    mock_user.save = MagicMock()

    with patch('user_profile.api.User.objects.aget', AsyncMock(return_value=mock_user)), \
            patch('user_profile.api.default_token_generator.check_token', return_value=True):
        uidb64 = urlsafe_base64_encode(force_bytes(str(mock_user.pk)))

        try:
            payload = PasswordResetSchema(new_password="")
            response = await password_reset_confirm_post(request, uidb64, 'mocktoken', payload)
        except ValidationError as e:
            response = JsonResponse({"error": str(e)}, status=400)

        assert response.status_code == 400
        assert response.content in b'{"error": "1 validation error for PasswordResetSchema\\nnew_password\\n  String should have at least 8 characters [type=string_too_short, input_value=\'\', input_type=str]\\n    For further information visit https://errors.pydantic.dev/2.8/v/string_too_short"}'
