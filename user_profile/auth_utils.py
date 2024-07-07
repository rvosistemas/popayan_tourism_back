from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from utils.logger import app_logger
from .models import User


def authenticate_user(username, password) -> User:
    user = authenticate(username=username, password=password)
    app_logger.info("User authenticated")
    if user is not None:
        return user
    else:
        app_logger.error("Invalid credentials")
        raise ValueError("Invalid credentials")


def generate_token(user) -> str:
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    app_logger.info("token generated")
    return token


def handle_login(username, password) -> Response:
    if not username or not password:
        app_logger.error("Username and password are required")
        raise ValueError("Username and password are required")

    user = authenticate_user(username, password)
    token = generate_token(user)
    app_logger.info("User logged in")
    return Response({'token': token})
