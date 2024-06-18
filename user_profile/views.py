# En tu archivo views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import UserSerializer
from .exceptions import handle_exceptions
from .models import User


def authenticate_user(username, password) -> User:
    user = authenticate(username=username, password=password)
    if user is not None:
        return user
    else:
        raise ValueError("Invalid credentials")


def generate_token(user) -> str:
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


@handle_exceptions
def handle_login(username, password) -> Response:
    if not username or not password:
        raise ValueError("Username and password are required")

    user = authenticate_user(username, password)
    token = generate_token(user)
    return Response({'token': token})


class LoginView(APIView):

    @staticmethod
    @swagger_auto_schema(
        operation_description="User login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            }
        ),
        responses={
            200: openapi.Response('Login successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT token')
                }
            )),
            400: 'Bad Request'
        }
    )
    def post(request) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')

        return handle_login(username, password)


class RegisterView(APIView):
    @staticmethod
    @handle_exceptions
    @swagger_auto_schema(
        operation_description="User registration",
        request_body=UserSerializer,
        responses={
            201: UserSerializer,
            400: 'Bad Request'
        }
    )
    def post(request) -> Response:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
