import json
from uuid import UUID, uuid4

import pytest
import httpx
from unittest.mock import patch, MagicMock
from django.core.asgi import get_asgi_application
from django.http import JsonResponse
from pydantic import UUID4

from cultural_places.api import create_cultural_place
from cultural_places.models import CulturalPlace, UserPlacePreference
from cultural_places.pydantic_serializers import CulturalPlaceSchema
from cultural_places.serializers import CulturalPlaceSerializer
from user_profile.models import User


@pytest.fixture
def mock_user():
    return MagicMock(spec=User, id=1, username="test_user", is_superuser=True)


@pytest.fixture
def mock_request(mock_user):
    request = MagicMock()
    request.user = mock_user
    return request


@pytest.fixture
def mock_token(mock_user):
    with patch('user_profile.auth_utils.generate_token', return_value='mock_token'), \
            patch('user_profile.auth.JWTAuth.authenticate', return_value=mock_user):
        yield 'mock_token'


@pytest.mark.asyncio
async def test_get_cultural_places_superuser(mock_token):
    """
    Prueba la función get_cultural_places cuando el usuario es superusuario.

    Simula el comportamiento de la función y verifica que la respuesta sea correcta.
    """
    cultural_places_mock = [
        MagicMock(
            name="Museo de Historia Natural",
            description="Un museo que alberga exposiciones de historia natural y paleontología.",
            address="Av. Central 45, Barrio Centro 2222",
            opening_hours={
                "monday": "09:00-17:00",
                "tuesday": "09:00-17:00",
                "wednesday": "09:00-17:00",
                "thursday": "09:00-17:00",
                "friday": "09:00-17:00",
                "saturday": "10:00-18:00",
                "sunday": "closed"
            },
            image=None,
            active=False
        ),
        MagicMock(
            name="Museo de Historia Natural 2",
            description="Un museo que alberga exposiciones de historia natural y paleontología.",
            address="Av. Central 45, Barrio Centro",
            opening_hours={
                "monday": "09:00-17:00",
                "tuesday": "09:00-17:00",
                "wednesday": "09:00-17:00",
                "thursday": "09:00-17:00",
                "friday": "09:00-17:00",
                "saturday": "10:00-18:00",
                "sunday": "closed"
            },
            image=None,
            active=True
        ),
    ]

    for place in cultural_places_mock:
        place.name = str(place.name)
        place.description = str(place.description)
        place.address = str(place.address)
        place.opening_hours = dict(place.opening_hours)
        place.image = None
        place.active = bool(place.active)

    mock_all = MagicMock(return_value=cultural_places_mock)

    with patch('cultural_places.models.CulturalPlace.objects.all', mock_all):
        with patch('cultural_places.api.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = cultural_places_mock
            mock_page.number = 1
            mock_page.__iter__.return_value = iter(cultural_places_mock)

            mock_paginator_instance = MagicMock()
            mock_paginator_instance.page.return_value = mock_page
            mock_paginator_instance.count = len(cultural_places_mock)
            mock_paginator_instance.num_pages = 1
            mock_paginator.return_value = mock_paginator_instance

            app = get_asgi_application()

            async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
                response = await async_client.get(
                    '/cultural_places/api/',
                    params={'page': 1, 'per_page': 10},
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict), "La respuesta debe ser un diccionario"
            assert data['total'] == 2
            assert data['num_pages'] == 1
            assert data['current_page'] == 1
            assert len(data['cultural_places']) == 2


@pytest.mark.asyncio
async def test_get_cultural_places_regular_user(mock_token, mock_user):
    """
    Prueba la función get_cultural_places cuando el usuario NO es superusuario.

    Simula el comportamiento de la función y verifica que la respuesta sea correcta.
    """
    mock_user.is_superuser = False

    cultural_places_mock = [
        CulturalPlace(
            name="Museo de Historia Natural",
            description="Un museo que alberga exposiciones de historia natural y paleontología.",
            address="Av. Central 45, Barrio Centro 2222",
            opening_hours={
                "monday": "09:00-17:00",
                "tuesday": "09:00-17:00",
                "wednesday": "09:00-17:00",
                "thursday": "09:00-17:00",
                "friday": "09:00-17:00",
                "saturday": "10:00-18:00",
                "sunday": "closed"
            },
            image=None,
            active=True
        )
    ]

    mock_filter = MagicMock(return_value=cultural_places_mock)

    with patch('cultural_places.models.CulturalPlace.objects.filter', mock_filter):
        with patch('cultural_places.api.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = cultural_places_mock
            mock_page.number = 1
            mock_page.__iter__.return_value = iter(cultural_places_mock)

            mock_paginator_instance = MagicMock()
            mock_paginator_instance.page.return_value = mock_page
            mock_paginator_instance.count = len(cultural_places_mock)
            mock_paginator_instance.num_pages = 1
            mock_paginator.return_value = mock_paginator_instance

            app = get_asgi_application()

            async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
                response = await async_client.get(
                    '/cultural_places/api/',
                    params={'page': 1, 'per_page': 10},
                    headers={"Authorization": f"Bearer {mock_token}"}
                )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict), "La respuesta debe ser un diccionario"
            assert data['total'] == 1
            assert data['current_page'] == 1
            assert len(data['cultural_places']) == 1
            assert data['cultural_places'][0]['name'] == "Museo de Historia Natural"
            assert data['cultural_places'][0]['active'] is True


@pytest.mark.asyncio
async def test_get_cultural_place_superuser(mock_token, mock_user):
    """
    Prueba la función get_cultural_place cuando el usuario es superusuario.

    Simula el comportamiento de la función y verifica que la respuesta sea correcta.
    """
    mock_user.is_superuser = True

    place_id = "123e4567-e89b-12d3-a456-426614174000"

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.name = "Museo de Historia Natural"
    cultural_place_mock.description = "Un museo que alberga exposiciones de historia natural y paleontología."
    cultural_place_mock.address = "Av. Central 45, Barrio Centro 2222"
    cultural_place_mock.opening_hours = {
        "monday": "09:00-17:00",
        "tuesday": "09:00-17:00",
        "wednesday": "09:00-17:00",
        "thursday": "09:00-17:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-18:00",
        "sunday": "closed"
    }
    cultural_place_mock.image = None
    cultural_place_mock.active = True

    mock_get = MagicMock(return_value=cultural_place_mock)

    with patch('cultural_places.models.CulturalPlace.objects.get', mock_get):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.get(
                f'/cultural_places/api/cultural_place/{place_id}',
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == "Museo de Historia Natural"
        assert data['active'] is True
        assert data['description'] == "Un museo que alberga exposiciones de historia natural y paleontología."


@pytest.mark.asyncio
async def test_get_cultural_place_regular_user(mock_token, mock_user):
    """
    Prueba la función get_cultural_place cuando el usuario NO es superusuario.

    Simula el comportamiento de la función y verifica que la respuesta sea correcta.
    """
    mock_user.is_superuser = False

    place_id = "123e4567-e89b-12d3-a456-426614174000"

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.name = "Museo de Historia Natural"
    cultural_place_mock.description = "Un museo que alberga exposiciones de historia natural y paleontología."
    cultural_place_mock.address = "Av. Central 45, Barrio Centro 2222"
    cultural_place_mock.opening_hours = {
        "monday": "09:00-17:00",
        "tuesday": "09:00-17:00",
        "wednesday": "09:00-17:00",
        "thursday": "09:00-17:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-18:00",
        "sunday": "closed"
    }
    cultural_place_mock.image = None
    cultural_place_mock.active = True

    mock_get = MagicMock(return_value=cultural_place_mock)

    with patch('cultural_places.models.CulturalPlace.objects.get', mock_get):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.get(
                f'/cultural_places/api/cultural_place/{place_id}',
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == "Museo de Historia Natural"
        assert data['active'] is True
        assert data['description'] == "Un museo que alberga exposiciones de historia natural y paleontología."


@pytest.mark.asyncio
async def test_create_cultural_place(mock_request):
    payload = {
        "name": "Museo de Historia Natural 2",
        "description": "Un museo que alberga exposiciones de historia natural y paleontología.",
        "address": "Av. Central 45, Barrio Centro",
        "opening_hours": {
            "monday": "09:00-17:00",
            "tuesday": "09:00-17:00",
            "wednesday": "09:00-17:00",
            "thursday": "09:00-17:00",
            "friday": "09:00-17:00",
            "saturday": "10:00-18:00",
            "sunday": "closed"
        },
        "image": None
    }

    schema_instance = CulturalPlaceSchema(**payload)

    mock_serializer = MagicMock(spec=CulturalPlaceSerializer)
    mock_serializer.is_valid.return_value = True
    mock_serializer.save.return_value = CulturalPlace(**payload)
    mock_serializer.data = payload

    with patch('cultural_places.api.CulturalPlaceSerializer', return_value=mock_serializer), \
            patch('asgiref.sync.sync_to_async', side_effect=lambda f: f):
        response = await create_cultural_place(mock_request, schema_instance)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}. Response content: {response.content}"

    data = json.loads(response.content.decode('utf-8'))

    assert data['detail'] == "Cultural place created"
    assert data['place']['name'] == payload['name']
    assert data['place']['description'] == payload['description']
    assert data['place']['address'] == payload['address']
    assert data['place']['opening_hours'] == payload['opening_hours']
    assert data['place']['image'] is None

    mock_serializer.is_valid.assert_called_once()
    mock_serializer.save.assert_called_once_with(created_by=mock_request.user, updated_by=mock_request.user)


@pytest.mark.asyncio
async def test_update_cultural_place_superuser(mock_request, mock_token):
    """
    Prueba la función update_cultural_place cuando el usuario es superusuario.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"
    payload = {
        "name": "Museo de Historia Natural Actualizado",
        "description": "Un museo renovado que alberga nuevas exposiciones de historia natural.",
        "address": "Av. Nueva 123, Barrio Moderno",
        "opening_hours": {
            "monday": "10:00-18:00",
            "tuesday": "10:00-18:00",
            "wednesday": "10:00-18:00",
            "thursday": "10:00-18:00",
            "friday": "10:00-18:00",
            "saturday": "11:00-19:00",
            "sunday": "closed"
        },
        "image": None
    }

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.name = "Museo de Historia Natural"
    cultural_place_mock.description = "Un museo que alberga exposiciones de historia natural y paleontología."
    cultural_place_mock.address = "Av. Central 45, Barrio Centro 2222"
    cultural_place_mock.opening_hours = {
        "monday": "09:00-17:00",
        "tuesday": "09:00-17:00",
        "wednesday": "09:00-17:00",
        "thursday": "09:00-17:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-18:00",
        "sunday": "closed"
    }
    cultural_place_mock.image = None
    cultural_place_mock.active = True
    cultural_place_mock.created_by = mock_request.user

    def mock_save(updated_by):
        cultural_place_mock.name = payload["name"]
        cultural_place_mock.description = payload["description"]
        cultural_place_mock.address = payload["address"]
        cultural_place_mock.opening_hours = payload["opening_hours"]
        cultural_place_mock.image = payload["image"]
        cultural_place_mock.updated_by = updated_by
        return cultural_place_mock

    with patch('cultural_places.api.get_object_or_404', return_value=cultural_place_mock), \
            patch('cultural_places.api.CulturalPlaceSerializer') as mock_serializer_class:
        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = True
        mock_serializer.save.side_effect = mock_save

        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.put(
                f'/cultural_places/api/cultural_place/{place_id}',
                json=payload,
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data['detail'] == f"Cultural place {place_id} updated"
        assert data['place']['name'] == payload['name']
        assert data['place']['description'] == payload['description']
        assert data['place']['address'] == payload['address']
        assert data['place']['opening_hours'] == payload['opening_hours']
        assert data['place']['image'] is None

        mock_serializer.is_valid.assert_called_once()
        mock_serializer.save.assert_called_once_with(updated_by=mock_request.user)


@pytest.mark.asyncio
async def test_update_cultural_place_regular_user_no_permission(mock_request, mock_token):
    """
    Prueba que un usuario regular no puede actualizar un lugar cultural creado por otro usuario.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_request.user.is_superuser = False
    payload = {
        "name": "Museo de Historia Natural Actualizado",
        "description": "Un museo renovado que alberga nuevas exposiciones de historia natural.",
        "address": "Av. Nueva 123, Barrio Moderno",
        "opening_hours": {
            "monday": "10:00-18:00",
            "tuesday": "10:00-18:00",
            "wednesday": "10:00-18:00",
            "thursday": "10:00-18:00",
            "friday": "10:00-18:00",
            "saturday": "11:00-19:00",
            "sunday": "closed"
        },
        "image": None
    }

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.created_by = MagicMock(id=2)
    cultural_place_mock.active = True

    with patch('cultural_places.api.get_object_or_404', return_value=cultural_place_mock):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.put(
                f'/cultural_places/api/cultural_place/{place_id}',
                json=payload,
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 403
        data = response.json()
        assert data['error'] == "You do not have permission to update this cultural place"


@pytest.mark.asyncio
async def test_delete_cultural_place_superuser(mock_request, mock_token):
    """
    Prueba la función delete_cultural_place cuando el usuario es superusuario.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.active = True
    cultural_place_mock.created_by = mock_request.user

    cultural_place_mock.delete = MagicMock()

    with patch('cultural_places.api.get_object_or_404', return_value=cultural_place_mock):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.delete(
                f'/cultural_places/api/cultural_place/{place_id}',
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 204
        data = response.json()
        assert data['detail'] == f"Cultural place {place_id} deleted"

        cultural_place_mock.delete.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_cultural_place_superuser(mock_request, mock_token):
    """
    Prueba la función deactivate_cultural_place cuando el usuario es superusuario y el lugar cultural está activo.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.name = "Museo de Historia Natural"
    cultural_place_mock.description = "Un museo que alberga exposiciones de historia natural y paleontología."
    cultural_place_mock.address = "Av. Central 45, Barrio Centro 2222"
    cultural_place_mock.opening_hours = {
        "monday": "09:00-17:00",
        "tuesday": "09:00-17:00",
        "wednesday": "09:00-17:00",
        "thursday": "09:00-17:00",
        "friday": "09:00-17:00",
        "saturday": "10:00-18:00",
        "sunday": "closed"
    }
    cultural_place_mock.image = None
    cultural_place_mock.active = True
    cultural_place_mock.created_by = mock_request.user

    with patch('cultural_places.api.get_object_or_404', return_value=cultural_place_mock):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.patch(
                f'/cultural_places/api/cultural_place/{place_id}/deactivate',
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data['detail'] == f"Cultural place {place_id} deactivated"
        assert data['place']['name'] == cultural_place_mock.name

        assert cultural_place_mock.active is False
        assert cultural_place_mock.updated_by == mock_request.user
        cultural_place_mock.save.assert_called_once()


@pytest.mark.asyncio
async def test_delete_cultural_place_not_superuser(mock_request, mock_token):
    """
    Prueba la función delete_cultural_place cuando el usuario NO es superusuario.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"

    mock_request.user.is_superuser = False

    app = get_asgi_application()

    async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
        response = await async_client.delete(
            f'/cultural_places/api/cultural_place/{place_id}',
            headers={"Authorization": f"Bearer {mock_token}"}
        )

    assert response.status_code == 403
    data = response.json()
    assert data['error'] == "You do not have permission to delete this cultural place"


@pytest.mark.asyncio
async def test_deactivate_cultural_place_not_superuser(mock_request, mock_token):
    """
    Prueba la función deactivate_cultural_place cuando el usuario NO es superusuario.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"

    mock_request.user.is_superuser = False

    app = get_asgi_application()

    async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
        response = await async_client.patch(
            f'/cultural_places/api/cultural_place/{place_id}/deactivate',
            headers={"Authorization": f"Bearer {mock_token}"}
        )

    assert response.status_code == 403
    data = response.json()
    assert data['error'] == "You do not have permission to deactivate this cultural place"


@pytest.mark.asyncio
async def test_deactivate_cultural_place_already_deactivated(mock_request, mock_token):
    """
    Prueba la función deactivate_cultural_place cuando el lugar cultural ya está desactivado.
    """
    place_id = "123e4567-e89b-12d3-a456-426614174000"

    cultural_place_mock = MagicMock()
    cultural_place_mock.id = place_id
    cultural_place_mock.active = False
    cultural_place_mock.created_by = mock_request.user

    with patch('cultural_places.api.get_object_or_404', return_value=cultural_place_mock):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.patch(
                f'/cultural_places/api/cultural_place/{place_id}/deactivate',
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == "Cultural place is already deactivated"


@pytest.mark.asyncio
async def test_create_user_place_preference(mock_request, mock_token):
    """
    Prueba la función create_user_place_preference cuando se crea una nueva preferencia de usuario.
    """
    user_uuid = uuid4()
    mock_request.user.id = user_uuid

    place_uuid = uuid4()

    payload = {
        "place": str(place_uuid),
        "rating": 5
    }

    user_place_preference_mock = MagicMock(spec=UserPlacePreference)
    user_place_preference_mock.user = user_uuid
    user_place_preference_mock.place = place_uuid
    user_place_preference_mock.rating = payload['rating']

    with patch('cultural_places.models.UserPlacePreference.objects.update_or_create',
               return_value=(user_place_preference_mock, True)):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.post(
                '/cultural_places/api/user_place_preference/',
                json=payload,
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data['place'] == str(place_uuid)
        assert data['rating'] == payload['rating']


@pytest.mark.asyncio
async def test_update_user_place_preference(mock_request, mock_token):
    """
    Prueba la función create_user_place_preference cuando se actualiza una preferencia de usuario existente.
    """
    user_uuid = uuid4()
    place_uuid = uuid4()

    mock_request.user.id = str(user_uuid)

    payload = {
        "place": str(place_uuid),
        "rating": 4
    }

    user_place_preference_mock = MagicMock(spec=UserPlacePreference)
    user_place_preference_mock.user = user_uuid
    user_place_preference_mock.place = place_uuid
    user_place_preference_mock.rating = payload['rating']

    with patch('cultural_places.models.UserPlacePreference.objects.update_or_create',
               return_value=(user_place_preference_mock, False)):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.post(
                '/cultural_places/api/user_place_preference/',
                json=payload,
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data['user'] == str(user_uuid)
        assert data['place'] == payload['place']
        assert data['rating'] == payload['rating']


@pytest.mark.asyncio
async def test_get_user_place_preferences(mock_request, mock_token):
    """
    Prueba la función get_user_place_preferences para obtener las preferencias de lugar de un usuario.
    """
    user_uuid = uuid4()
    place_uuid = uuid4()

    mock_request.user.id = str(user_uuid)

    payload = {
        "place": str(place_uuid),
        "rating": 5
    }

    user_place_preference_mock = MagicMock(spec=UserPlacePreference)
    user_place_preference_mock.user = user_uuid
    user_place_preference_mock.place = place_uuid
    user_place_preference_mock.rating = payload['rating']

    mock_queryset = [user_place_preference_mock]

    with patch('cultural_places.models.UserPlacePreference.objects.filter', return_value=mock_queryset):
        app = get_asgi_application()

        async with httpx.AsyncClient(app=app, base_url="http://testserver") as async_client:
            response = await async_client.get(
                '/cultural_places/api/user_place_preferences/',
                headers={"Authorization": f"Bearer {mock_token}"}
            )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert len(data) == 1
        assert data[0]['user'] == str(user_uuid)
        assert data[0]['place'] == str(place_uuid)
        assert data[0]['rating'] == 5




