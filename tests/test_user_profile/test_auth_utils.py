import pytest
import json
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from user_profile.auth_utils import (
    authenticate_user,
    generate_token,
    handle_login,
    generate_password_reset_token,
    send_password_reset_email
)


@pytest.mark.asyncio
@patch('user_profile.auth_utils.authenticate', return_value=MagicMock(spec=User))
async def test_authenticate_user(mock_authenticate):
    user = await authenticate_user('testuser', 'testpassword')
    assert user is not None
    mock_authenticate.assert_called_once_with(username='testuser', password='testpassword')


@pytest.mark.asyncio
@patch('user_profile.auth_utils.authenticate', return_value=None)
@patch('user_profile.auth_utils.app_logger.error')
async def test_authenticate_user_invalid_credentials(mock_logger, mock_authenticate):
    with pytest.raises(ValueError, match="Invalid credentials"):
        await authenticate_user('testuser', 'wrongpassword')

    mock_authenticate.assert_called_once_with(username='testuser', password='wrongpassword')
    mock_logger.assert_called_once_with("Invalid credentials")


@pytest.mark.asyncio
@patch('user_profile.auth_utils.api_settings.JWT_PAYLOAD_HANDLER', return_value={'user_id': 1})
@patch('user_profile.auth_utils.api_settings.JWT_ENCODE_HANDLER', return_value='testtoken')
async def test_generate_token(mock_jwt_payload, mock_jwt_encode):
    user = MagicMock(spec=User)
    token = await generate_token(user)

    assert token == 'testtoken'


@pytest.mark.asyncio
@patch('user_profile.auth_utils.authenticate_user', return_value=MagicMock(spec=User))
@patch('user_profile.auth_utils.generate_token', return_value='testtoken')
async def test_handle_login(mock_authenticate_user, mock_generate_token):
    response = await handle_login('testuser', 'testpassword')

    assert isinstance(response, JsonResponse)
    assert response.status_code == 200

    response_data = json.loads(response.content)

    assert response_data == {'token': 'testtoken'}


@pytest.mark.asyncio
@patch('user_profile.auth_utils.app_logger.error')
async def test_handle_login_no_username(mock_logger):
    with pytest.raises(ValueError, match="Username and password are required"):
        await handle_login('', 'testpassword')

    mock_logger.assert_called_once_with("Username and password are required")


@pytest.mark.asyncio
@patch('user_profile.auth_utils.app_logger.error')
async def test_handle_login_no_password(mock_logger):
    with pytest.raises(ValueError, match="Username and password are required"):
        await handle_login('testuser', '')

    mock_logger.assert_called_once_with("Username and password are required")


@patch('user_profile.auth_utils.default_token_generator.make_token', return_value='testtoken')
def test_generate_password_reset_token(mock_make_token):
    user = MagicMock(spec=User)
    uid, token = generate_password_reset_token(user)
    assert uid == urlsafe_base64_encode(force_bytes(user.pk))
    assert token == 'testtoken'
    mock_make_token.assert_called_once_with(user)


@patch('user_profile.auth_utils.EmailMultiAlternatives')
@patch('user_profile.auth_utils.render_to_string', return_value='rendered_message')
@patch('user_profile.auth_utils.os.getenv', return_value='from@example.com')
def test_send_password_reset_email(mock_getenv, mock_render_to_string, mock_email_multi_alternatives):
    user = MagicMock(spec=User)
    user.username = 'testuser'
    user.email = 'test@example.com'
    reset_link = 'http://example.com/reset'

    mock_msg = mock_email_multi_alternatives.return_value
    mock_msg.send = MagicMock()

    send_password_reset_email(user, reset_link)

    mock_render_to_string.assert_called_once_with('reset_password_email.html', {
        'user': user,
        'reset_link': reset_link,
    })
    mock_getenv.assert_called_once_with('EMAIL_HOST_USER')
    mock_email_multi_alternatives.assert_called_once_with(
        'Password Reset Request',
        f"Hello testuser,\nYou requested a password reset. Click the link below to reset your "
        f"password:\n{reset_link}\nIf you did not request this, please ignore this email.",
        'from@example.com',
        [user.email]
    )
    mock_msg.attach_alternative.assert_called_once_with('rendered_message', "text/html")
    mock_msg.send.assert_called_once()
