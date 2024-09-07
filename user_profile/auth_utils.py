import os
from datetime import datetime, timedelta, timezone

import jwt
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode

from project import settings
from utils.logger import app_logger
from .models import User


async def authenticate_user(username, password) -> User:
    user = await sync_to_async(authenticate)(username=username, password=password)
    if user is not None:
        return user
    else:
        app_logger.error("Invalid credentials")
        raise ValueError("Invalid credentials")


async def generate_token(user) -> str:
    payload = {
        'user_id': str(user.id),
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    token_str = token.decode('utf-8') if isinstance(token, bytes) else token
    app_logger.info("Generated token")
    return token_str


async def handle_login(username, password) -> JsonResponse:
    if not all(isinstance(var, str) and var for var in [username, password]):
        app_logger.error("Username and password must be non-empty strings")
        raise ValueError("Username and password must be non-empty strings")

    user = await authenticate_user(username, password)
    token = await generate_token(user)
    app_logger.info("User logged in")
    return JsonResponse({'token': token}, status=200)


def generate_password_reset_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def send_password_reset_email(user, reset_link):
    mail_subject = 'Password Reset Request'
    message = render_to_string('reset_password_email.html', {
        'user': user,
        'reset_link': reset_link,
    })
    app_logger.info("Message rendered")
    from_email = os.getenv('EMAIL_HOST_USER')
    to_email = user.email
    app_logger.info("Get email to and from")
    text_content = (f"Hello {user.username},\nYou requested a password reset. Click the link below to reset your "
                    f"password:\n{reset_link}\nIf you did not request this, please ignore this email.")
    app_logger.info("Before create email")
    msg = EmailMultiAlternatives(mail_subject, text_content, from_email, [to_email])
    msg.attach_alternative(message, "text/html")
    app_logger.info("Before send email")
    msg.send()
    app_logger.info(f"Password reset link sent to {to_email}")
