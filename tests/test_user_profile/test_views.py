import pytest
from unittest.mock import patch, MagicMock

from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.exceptions import ValidationError


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123',
        'date_of_birth': '2000-01-01'
    }


@pytest.mark.asyncio
async def test_login_view():
    async def mock_handle_login():
        return Response({'token': 'test_token'}, status=status.HTTP_200_OK)

    with patch('user_profile.views.handle_login', new=mock_handle_login):
        client = APIClient()
        url = reverse('login')
        request_data = {'username': 'test', 'password': 'test'}

        response = await sync_to_async(client.post)(url, request_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'token': 'test_token'}


@patch('user_profile.serializers.UserSerializer.is_valid', return_value=True)
@patch('user_profile.serializers.UserSerializer.save', return_value=MagicMock())
@patch('user_profile.serializers.UserSerializer')
@patch('user_profile.models.User.objects.create_user', return_value=MagicMock())
@patch('user_profile.models.User.objects.filter')
def test_register_view(mock_user_filter, mock_user_create, mock_user_serializer_class, mock_save, mock_is_valid, api_rf,
                       user_data):
    # Configurar el mock para que retorne un queryset vacío simulando que el usuario no existe
    mock_user_filter.return_value.exists.return_value = False

    mock_serializer_instance = mock_user_serializer_class.return_value
    mock_serializer_instance.data = user_data
    mock_serializer_instance.validated_data = user_data  # Ensure validated_data returns the correct values
    mock_serializer_instance.is_valid.return_value = True  # Ensure is_valid returns True

    # Configurar explícitamente los valores de los campos en el mock del serializador
    mock_serializer_instance.data['username'] = 'testuser'
    mock_serializer_instance.data['email'] = 'testuser@example.com'
    mock_serializer_instance.data['date_of_birth'] = '2000-01-01'
    mock_serializer_instance.data['password'] = 'password123'

    mock_serializer_instance.validated_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'date_of_birth': '2000-01-01',
        'password': 'password123'
    }

    request = api_rf.post('/api/register/', user_data, format='json')
    view = RegisterView.as_view()
    response = view(request)

    expected_result = user_data  # Esperamos los datos del usuario

    assert response.status_code == 201, f"Response data: {response.data}"
    # assert response.data == expected_result, f"Response data: {response.data}"
    # mock_user_serializer_class.assert_called_once_with(data=user_data)
    # mock_is_valid.assert_called_once_with(raise_exception=True)
    # mock_save.assert_called_once()
    # mock_user_create.assert_called_once()
    # mock_user_filter.assert_called()


@patch('user_profile.views.authenticate_user', side_effect=ValueError("Invalid credentials"))
def test_login_view_invalid_credentials(mock_authenticate_user, api_rf):
    request = api_rf.post('/api/login/', {'username': 'testuser', 'password': 'wrongpassword'}, format='json')
    view = LoginView.as_view()
    response = view(request)

    assert response.status_code == 400
    assert response.data == {'error': 'Invalid credentials'}
    mock_authenticate_user.assert_called_once_with('testuser', 'wrongpassword')


@patch('user_profile.serializers.UserSerializer.is_valid', side_effect=ValidationError({'error': 'Invalid data'}))
def test_register_view_invalid_data(mock_is_valid, api_rf, user_data):
    request = api_rf.post('/api/register/', user_data, format='json')
    view = RegisterView.as_view()
    response = view(request)

    assert response.status_code == 400
    # assert response.data == {'error': 'Invalid data'}
    # mock_is_valid.assert_called_once_with(raise_exception=True)
