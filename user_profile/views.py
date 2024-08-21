import json
from asgiref.sync import sync_to_async
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from utils.logger import app_logger
from .serializers import UserSerializer
from .exceptions import async_handle_exceptions
from .swagger import (
    user_login_swagger_params,
    user_registration_swagger_params,
    password_reset_request_swagger_params,
    password_reset_confirm_swagger_params,
)
from .auth_utils import handle_login, send_password_reset_email, generate_password_reset_token
from .models import User


class LoginView(View):

    @async_handle_exceptions
    @swagger_auto_schema(**user_login_swagger_params)
    async def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        response = await handle_login(username, password)
        return response


class RegisterView(View):
    @async_handle_exceptions
    @swagger_auto_schema(**user_registration_swagger_params)
    async def post(self, request) -> JsonResponse:
        data = json.loads(request.body.decode('utf-8'))
        serializer = UserSerializer(data=data)

        is_valid = await sync_to_async(serializer.is_valid)(raise_exception=True)
        if is_valid:
            await sync_to_async(serializer.save)()
            app_logger.info("User registered")
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)


class PasswordResetRequestView(View):

    @async_handle_exceptions
    @swagger_auto_schema(**password_reset_request_swagger_params)
    async def post(self, request) -> JsonResponse:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        if not email:
            app_logger.error("Email is required")
            return JsonResponse({'error': 'Email is required'}, status=400)

        try:
            user = await User.objects.aget(email=email)
        except ObjectDoesNotExist:
            app_logger.error("User with this email does not exist")
            return JsonResponse({'error': 'User with this email does not exist'}, status=400)

        uid, token = generate_password_reset_token(user)
        reset_link = f"{request.scheme}://{request.get_host()}/user_profile/reset-password/{uid}/{token}/"
        send_password_reset_email(user, reset_link)

        return JsonResponse({'message': 'Password reset link sent'}, status=200)


class PasswordResetConfirmView(View):

    @async_handle_exceptions
    async def get(self, request, uidb64, token):
        app_logger.info("Get password reset link")
        context = {
            'uidb64': uidb64,
            'token': token,
            'csrf_token': get_token(request)
        }
        return await render(request, 'password_reset_confirm.html', context)

    @async_handle_exceptions
    @swagger_auto_schema(**password_reset_confirm_swagger_params)
    async def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            app_logger.info(f"Decoded uid: {uid}")
            user = await sync_to_async(User.objects.get)(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist) as e:
            user = None
            app_logger.error(f"Invalid user: {e}")

        if user is not None and default_token_generator.check_token(user, token):
            data = json.loads(request.body.decode('utf-8'))
            new_password = data.get('new_password')
            if new_password:
                user.set_password(new_password)
                await sync_to_async(user.save)()
                app_logger.info("Password has been reset")
                return JsonResponse({'message': 'Password has been reset'}, status=200)
            else:
                app_logger.error("Password is required")
                return JsonResponse({'error': 'Password is required'}, status=400)
        else:
            app_logger.error("Invalid token or user")
            return JsonResponse({'error': 'Invalid token or user'}, status=400)
