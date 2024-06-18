import pytest
from django.urls import resolve, reverse
from rest_framework import permissions
from unittest.mock import Mock
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from user_profile import views, urls


# Mock para las vistas de Django
class MockView:
    pass


# Mock para el schema_view de drf-yasg
def mock_schema_view(*args, **kwargs):
    return Mock()


# Fixture para schema_view mockeado
@pytest.fixture
def mock_schema_view(monkeypatch):
    monkeypatch.setattr(urls, 'schema_view', mock_schema_view)


# Fixture para el cliente de prueba de Django
@pytest.fixture
def client():
    from django.test.client import Client
    return Client()


# Prueba para verificar la URL de login
def test_login_url_resolves():
    url = reverse('login')
    assert resolve(url).func.view_class == views.LoginView


# Prueba para verificar la URL de registro
def test_register_url_resolves():
    url = reverse('register')
    assert resolve(url).func.view_class == views.RegisterView


# Prueba para verificar que las vistas de Swagger están configuradas correctamente
def test_swagger_urls(client):
    swagger_ui_url = reverse('schema-swagger-ui')
    response = client.get(swagger_ui_url)
    assert response.status_code == 200

    redoc_url = reverse('schema-redoc')
    response = client.get(redoc_url)
    assert response.status_code == 200

    swagger_json_url = reverse('schema-json')
    response = client.get(swagger_json_url)
    assert response.status_code == 200


# Prueba para verificar la configuración del schema_view
def test_schema_view(mock_schema_view):
    schema = get_schema_view()
    assert schema is mock_schema_view
