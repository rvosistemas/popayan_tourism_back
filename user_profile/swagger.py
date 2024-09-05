# swagger.py
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from .serializers import UserSerializer

schema_view = get_schema_view(
    openapi.Info(
        title="User Profile API",
        default_version='v1',
        description="Documentation of API User Profile",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourproject.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

user_login_swagger_params = {
    'operation_description': "User login",
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
        }
    ),
    'responses': {
        200: openapi.Response('Login successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT token')
            }
        )),
        400: 'Bad Request'
    }
}

user_registration_swagger_params = {
    'operation_description': "User registration",
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'password', 'date_of_birth'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format='password', description='User password'),
            'date_of_birth': openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                description='Date of birth in format YYYY-MM-DD')
        }
    ),
    'responses': {
        201: UserSerializer,
        400: 'Bad Request'
    }
}

password_reset_request_swagger_params = {
    'operation_description': "Request password reset",
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email')
        }
    ),
    'responses': {
        200: openapi.Response('Password reset link sent'),
        400: 'Bad Request'
    }
}

password_reset_confirm_swagger_params = {
    'operation_description': "Confirm password reset",
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['new_password'],
        properties={
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New Password')
        }
    ),
    'responses': {
        200: openapi.Response('Password has been reset'),
        400: 'Bad Request'
    }
}
