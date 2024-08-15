from django.urls import reverse, resolve
from user_profile import views


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

