# views.py
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
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
from .auth_utils import handle_login
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

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
        mail_subject = 'Password Reset Request'
        message = render_to_string('reset_password_email.html', {
            'user': user,
            'reset_link': reset_link,
        })
        send_mail(mail_subject, message, 'dark_rd@hotmail.com', [email])
        app_logger.info(f"Password reset link sent to {email}")
        return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

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
