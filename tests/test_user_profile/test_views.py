import uuid
import pytest
import json
from unittest.mock import patch, MagicMock
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.test import RequestFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from user_profile import views
from user_profile.models import User
from utils.logger import app_logger


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.pk = uuid.uuid4()
    user.username = "testuser"
    user.email = "test@example.com"
    return user


@pytest.mark.asyncio
async def test_login_view():
    async def mock_handle_login(username, password):
        return JsonResponse({'token': 'test_token'}, status=status.HTTP_200_OK)

    with patch('user_profile.views.handle_login', new=mock_handle_login):
        factory = APIRequestFactory()
        url = reverse('login')
        request_data = {'username': 'test', 'password': 'test'}

        request = factory.post(url, request_data, format='json')

        view = views.LoginView.as_view()
        response = await view(request)
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in json.loads(response.content)
        assert json.loads(response.content)['token'] == 'test_token'


@pytest.mark.asyncio
async def test_register_view():
    def mock_is_valid(*args, **kwargs):
        return True

    def mock_save(*args, **kwargs):
        return {'username': 'testuser', 'email': 'test@example.com'}

    with patch('user_profile.serializers.UserSerializer.is_valid', new=mock_is_valid):
        with patch('user_profile.serializers.UserSerializer.save', new=mock_save):
            with patch('user_profile.serializers.UserSerializer.data',
                       new_callable=lambda: {'username': 'testuser', 'email': 'test@example.com'}):
                factory = APIRequestFactory()
                url = reverse('register')
                request_data = {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'password123',
                    'date_of_birth': '2000-01-01'
                }

                request = factory.post(url, request_data, format='json')
                view = views.RegisterView.as_view()
                response = await view(request)

                assert response.status_code == 201
                assert 'username' in json.loads(response.content)
                assert json.loads(response.content)['username'] == 'testuser'


@pytest.mark.asyncio
async def test_register_view_invalid_data():
    def mock_is_valid(*args, **kwargs):
        return False

    def mock_errors(*args, **kwargs):
        return {'username': ['This field is required.']}

    with patch('user_profile.serializers.UserSerializer.is_valid', new=mock_is_valid):
        with patch('user_profile.serializers.UserSerializer.errors', new_callable=lambda: mock_errors()):
            factory = APIRequestFactory()
            url = reverse('register')
            request_data = {
                'email': 'test@example.com',
                'password': 'password123',
                'date_of_birth': '2000-01-01'
                # Missing 'username' field here to simulate invalid data
            }

            request = factory.post(url, request_data, format='json')
            view = views.RegisterView.as_view()
            response = await view(request)

            assert response.status_code == 400
            assert 'username' in json.loads(response.content)
            assert json.loads(response.content)['username'] == ['This field is required.']


@pytest.mark.asyncio
async def test_password_reset_request_view_success():
    async def mock_aget(*args, **kwargs):
        return User(username="testuser", email="test@example.com")

    with patch('user_profile.models.User.objects.aget', new=mock_aget):
        with patch('user_profile.views.generate_password_reset_token', return_value=('uid', 'token')):
            with patch('user_profile.views.send_password_reset_email') as mock_send_email:
                factory = APIRequestFactory()
                url = reverse('request-reset-password')
                request_data = {'email': 'test@example.com'}

                request = factory.post(url, request_data, format='json')
                view = views.PasswordResetRequestView.as_view()

                response = await view(request)

                assert response.status_code == 200
                assert mock_send_email.called


@pytest.mark.asyncio
async def test_password_reset_request_view_no_email():
    factory = APIRequestFactory()
    url = reverse('request-reset-password')
    request_data = {}  # No email provided

    request = factory.post(url, request_data, format='json')
    view = views.PasswordResetRequestView.as_view()
    response = await view(request)

    assert response.status_code == 400
    assert 'error' in json.loads(response.content)
    assert json.loads(response.content)['error'] == 'Email is required'


@pytest.mark.asyncio
async def test_password_reset_request_view_user_not_found():
    async def mock_aget(*args, **kwargs):
        raise ObjectDoesNotExist

    with patch('user_profile.models.User.objects.aget', new=mock_aget):
        factory = APIRequestFactory()
        url = reverse('request-reset-password')
        request_data = {'email': 'nonexistent@example.com'}

        request = factory.post(url, request_data, format='json')
        view = views.PasswordResetRequestView.as_view()
        response = await view(request)

        assert response.status_code == 400
        assert 'error' in json.loads(response.content)
        assert json.loads(response.content)['error'] == 'User with this email does not exist'


@pytest.mark.asyncio
async def test_password_reset_confirm_view_get():
    # Crear un usuario mock más completo
    mock_user = MagicMock(spec=User)
    mock_user.pk = 1
    mock_user.get_email_field_name.return_value = 'email'
    mock_user.email = 'test@example.com'
    mock_user.last_login = None
    mock_user.password = 'password_hash'

    uidb64 = urlsafe_base64_encode(force_bytes(mock_user.pk))
    token = default_token_generator.make_token(mock_user)

    url = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})

    request = RequestFactory().get(url)

    with patch('user_profile.views.get_token', return_value='mocked_csrf_token'):
        with patch('user_profile.views.render') as mock_render:
            mock_render.return_value = MagicMock()

            view = views.PasswordResetConfirmView.as_view()
            response = await view(request, uidb64=uidb64, token=token)

            mock_render.assert_called_once_with(
                request,
                'password_reset_confirm.html',
                {
                    'uidb64': uidb64,
                    'token': token,
                    'csrf_token': 'mocked_csrf_token'
                }
            )

    with patch('user_profile.views.app_logger.info') as mock_logger:
        await view(request, uidb64=uidb64, token=token)
        mock_logger.assert_called_once_with("Get password reset link")


@pytest.mark.asyncio
async def test_password_reset_confirm_view_success():
    user = User(pk=1, username="testuser", email="test@example.com")

    def mock_get(*args, **kwargs):
        app_logger.info(f"Mock get called with args: {args}, kwargs: {kwargs}")
        return user

    with patch('user_profile.models.User.objects.get', new=mock_get):
        with patch('user_profile.views.default_token_generator.check_token', return_value=True):
            factory = APIRequestFactory()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            app_logger.info(f"Generated uidb64: {uidb64}")
            token = default_token_generator.make_token(user)
            app_logger.info(f"Generated token: {token}")
            url = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
            request_data = {'new_password': 'new_password123'}

            request = factory.post(url, request_data, format='json')
            view = views.PasswordResetConfirmView.as_view()

            with patch('user_profile.models.User.save', return_value=None):
                response = await view(request, uidb64=uidb64, token=token)

            app_logger.info(f"Response status code: {response.status_code}")
            assert response.status_code == 200
            assert json.loads(response.content)['message'] == 'Password has been reset'


@pytest.mark.asyncio
async def test_password_reset_confirm_view_invalid_token():
    mock_user = MagicMock()
    mock_user.pk = 1

    with patch('user_profile.views.force_str', return_value=str(mock_user.pk)):
        with patch('user_profile.views.sync_to_async', side_effect=lambda f: f):
            with patch('user_profile.models.User.objects.get', return_value=mock_user):
                with patch('user_profile.views.default_token_generator.check_token', return_value=False):
                    factory = APIRequestFactory()
                    uidb64 = urlsafe_base64_encode(force_bytes(mock_user.pk))
                    token = 'invalid-token'
                    url = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
                    request_data = {'new_password': 'new_password123'}

                    request = factory.post(url, json.dumps(request_data), content_type='application/json')
                    view = views.PasswordResetConfirmView.as_view()

                    response = await view(request, uidb64=uidb64, token=token)

                    assert response.status_code == 400
                    assert json.loads(response.content)['error'] == 'Invalid token or user'


@pytest.mark.asyncio
async def test_password_reset_confirm_view_user_not_found():
    async def mock_get(*args, **kwargs):
        raise ObjectDoesNotExist()

    with patch('user_profile.models.User.objects.get', new=mock_get):
        with patch('user_profile.views.force_str', return_value='1'):
            factory = APIRequestFactory()
            uidb64 = urlsafe_base64_encode(force_bytes(1))
            token = default_token_generator.make_token(User(username="testuser"))
            url = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
            request_data = {'new_password': 'new_password123'}

            request = factory.post(url, json.dumps(request_data), content_type='application/json')
            view = views.PasswordResetConfirmView.as_view()

            response = await view(request, uidb64=uidb64, token=token)

            assert response.status_code == 400
            assert json.loads(response.content)['error'] == 'Invalid token or user'


@pytest.mark.asyncio
async def test_password_reset_confirm_view_no_password():
    mock_user = MagicMock(spec=User)
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.pk = 1
    mock_user.get_email_field_name.return_value = 'email'
    mock_user.last_login = None

    def mock_get(*args, **kwargs):
        return mock_user

    with patch('user_profile.models.User.objects.get', new=mock_get):
        with patch('user_profile.views.default_token_generator.check_token', return_value=True):
            with patch('user_profile.views.force_str', return_value='1'):
                factory = APIRequestFactory()
                uidb64 = urlsafe_base64_encode(force_bytes(1))
                token = default_token_generator.make_token(mock_user)
                url = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
                request_data = {}  # No password provided

                request = factory.post(url, json.dumps(request_data), content_type='application/json')
                view = views.PasswordResetConfirmView.as_view()

                response = await view(request, uidb64=uidb64, token=token)

                assert response.status_code == 400
                assert json.loads(response.content)['error'] == 'Password is required'
