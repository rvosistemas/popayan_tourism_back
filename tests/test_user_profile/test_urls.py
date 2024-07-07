import pytest
from django.urls import reverse, resolve
from unittest.mock import patch
from user_profile import views
from rest_framework.response import Response
from rest_framework import status


class TestUrls:

    def test_swagger_ui_url(self, client):
        url = reverse('schema-swagger-ui')
        response = client.get(url)
        assert response.status_code == 200

    def test_redoc_url(self, client):
        url = reverse('schema-redoc')
        response = client.get(url)
        assert response.status_code == 200

    def test_swagger_json_url(self, client):
        url = reverse('schema-json', kwargs={'format': '.json'})
        response = client.get(url)
        assert response.status_code == 200

    def test_login_url(self):
        path = reverse('login')
        assert resolve(path).func.view_class == views.LoginView

    def test_register_url(self):
        path = reverse('register')
        assert resolve(path).func.view_class == views.RegisterView

    @patch.object(views.LoginView, 'post')
    def test_login_view(self, mock_post, client):
        mock_post.return_value = Response(status=status.HTTP_200_OK)
        url = reverse('login')
        response = client.post(url, data={'username': 'test', 'password': 'test'})
        assert response.status_code == 200

    @patch.object(views.RegisterView, 'post')
    def test_register_view(self, mock_post, client):
        mock_post.return_value = Response(status=status.HTTP_200_OK)
        url = reverse('register')
        response = client.post(url, data={'username': 'test', 'password': 'test', 'email': 'test@example.com'})
        assert response.status_code == 200
