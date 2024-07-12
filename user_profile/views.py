# views.py
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from utils.logger import app_logger
from .serializers import UserSerializer
from .exceptions import handle_exceptions
from .swagger import (
    user_login_swagger_params,
    user_registration_swagger_params,
    password_reset_request_swagger_params,
    password_reset_confirm_swagger_params,
)
from .auth_utils import handle_login, send_password_reset_email, generate_password_reset_token
from .models import User


class LoginView(APIView):

    @swagger_auto_schema(**user_login_swagger_params)
    def post(self, request) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')

        return handle_login(username, password)


class RegisterView(APIView):
    @handle_exceptions
    @swagger_auto_schema(**user_registration_swagger_params)
    def post(self, request) -> Response:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            app_logger.info("User registered")
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    @handle_exceptions
    @swagger_auto_schema(**password_reset_request_swagger_params)
    def post(self, request):
        email = request.data.get('email')
        if not email:
            app_logger.error("Email is required")
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            app_logger.error("User with this email does not exist")
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        uid, token = generate_password_reset_token(user)
        reset_link = f"{request.scheme}://{request.get_host()}/user_profile/reset-password/{uid}/{token}/"
        send_password_reset_email(user, reset_link)

        return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    @handle_exceptions
    def get(self, request, uidb64, token):
        app_logger.info("Get password reset link")
        context = {
            'uidb64': uidb64,
            'token': token,
            'csrf_token': get_token(request)
        }
        return render(request, 'password_reset_confirm.html', context)

    @handle_exceptions
    @swagger_auto_schema(**password_reset_confirm_swagger_params)
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None
            app_logger.error("Invalid user")

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            if new_password:
                user.set_password(new_password)
                user.save()
                app_logger.info("Password has been reset")
                return Response({'message': 'Password has been reset'}, status=status.HTTP_200_OK)
            else:
                app_logger.error("Password is required")
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            app_logger.error("Invalid token or user")
            return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)
