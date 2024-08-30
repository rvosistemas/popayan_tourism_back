from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from cultural_places.serializers import CulturalPlaceSerializer

schema_view = get_schema_view(
    openapi.Info(
        title="Cultural Place API",
        default_version='v1',
        description="Documentation of API Cultural Place",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourproject.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.IsAuthenticated,)
)

get_cultural_places_swagger_params = {
    'operation_description': "Cultural places",
    'request_body': CulturalPlaceSerializer,
    'responses': {
        201: CulturalPlaceSerializer,
        400: 'Bad Request'
    }
}

get_cultural_place_swagger_params = {
    'operation_description': "Cultural place",
    'request_body': CulturalPlaceSerializer,
    'responses': {
        200: CulturalPlaceSerializer,
        400: 'Bad Request'
    }
}

post_cultural_place_swagger_params = {
    'operation_description': "Cultural place",
    'request_body': CulturalPlaceSerializer,
    'responses': {
        201: CulturalPlaceSerializer,
        400: 'Bad Request'
    }
}

put_cultural_place_swagger_params = {
    'operation_description': "Cultural place",
    'request_body': CulturalPlaceSerializer,
    'responses': {
        200: CulturalPlaceSerializer,
        400: 'Bad Request'
    }
}

delete_cultural_place_swagger_params = {
    'operation_description': "Cultural place",
    'request_body': CulturalPlaceSerializer,
    'responses': {
        200: CulturalPlaceSerializer,
        400: 'Bad Request'
    }
}