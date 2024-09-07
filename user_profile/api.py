# user_profile/api.py
import json

from django.http import JsonResponse
from ninja import NinjaAPI
from .models import User
from .auth_utils import (
    handle_login,
    send_password_reset_email,
    generate_password_reset_token
)
from utils.logger import app_logger
from utils.exceptions import async_handle_exceptions
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from asgiref.sync import sync_to_async

from .pydantic_serializers import UserLoginSchema, UserRegisterSchema, PasswordResetSuccessSchema, \
    PasswordResetErrorSchema, PasswordResetRequestSchema, PasswordResetSchema
from .serializers import UserSerializer

api = NinjaAPI(
    title="User Profile API",
    version="1.0",
    description="API for managing user profiles",
    urls_namespace='user_profile_api'
)


@api.post("/login", response={200: UserLoginSchema, 400: dict})
@async_handle_exceptions
async def login(request) -> JsonResponse:
    request_data = json.loads(request.body.decode('utf-8'))
    username = request_data.get('username')
    password = request_data.get('password')
    return await handle_login(username, password)


@api.post("/register", response={201: UserRegisterSchema, 400: dict})
@async_handle_exceptions
async def register(request, payload: UserRegisterSchema) -> JsonResponse:
    user_data = payload.dict()
    serializer = UserSerializer(data=user_data)
    is_valid = await sync_to_async(serializer.is_valid)()
    if is_valid:
        user = await sync_to_async(serializer.save)()
        app_logger.info("User registered")
        user_data = UserRegisterSchema.from_orm(user).dict()
        return JsonResponse(user_data, status=201)


@api.post("/request-reset-password", response={200: PasswordResetSuccessSchema, 400: PasswordResetErrorSchema})
@async_handle_exceptions
async def request_reset_password(
        request,
        payload: PasswordResetRequestSchema
):
    email = payload.email
    user = await User.objects.aget(email=email)

    uid, token = generate_password_reset_token(user)
    reset_link = f"{request.scheme}://{request.get_host()}/user_profile/reset-password/{uid}/{token}/"
    send_password_reset_email(user, reset_link)

    return PasswordResetSuccessSchema(message="Password reset link sent")


@api.get("/reset-password/{uidb64}/{token}", response={200: dict})
@async_handle_exceptions
async def password_reset_confirm_get(request, uidb64: str, token: str) -> dict:
    app_logger.info("Get password reset link")
    context = {
        'uidb64': uidb64,
        'token': token,
        'csrf_token': get_token(request)
    }
    return render(request, 'password_reset_confirm.html', context)


@api.post("/reset-password/{uidb64}/{token}", response={200: dict, 400: dict})
@async_handle_exceptions
async def password_reset_confirm_post(request, uidb64: str, token: str, payload: PasswordResetSchema):
    new_password = payload.new_password

    uid = force_str(urlsafe_base64_decode(uidb64))
    app_logger.info(f"Decoded uid: {uid}")

    user = await User.objects.aget(pk=uid)

    if user and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        await sync_to_async(user.save, thread_sensitive=True)()
        app_logger.info("Password has been reset")
        return JsonResponse({"message": "Password has been reset"}, status=200)
