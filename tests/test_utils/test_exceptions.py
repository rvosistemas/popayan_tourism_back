import pytest
import json

from django.core.paginator import PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from utils.exceptions import handle_exceptions, async_handle_exceptions, retry_with_page_one


def test_handle_exceptions_with_validation_error():
    # Crear una función mock que lanza una ValidationError
    @handle_exceptions
    def func_raises_validation_error():
        raise ValidationError('validation error occurred')

    response = func_raises_validation_error()

    expected_result = {'error': "[ErrorDetail(string='validation error occurred', code='invalid')]"}

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == expected_result


def test_handle_exceptions_with_value_error():
    @handle_exceptions
    def func_raises_value_error():
        raise ValueError('value error occurred')

    response = func_raises_value_error()

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'error': 'value error occurred'}


def test_handle_exceptions_with_general_exception():
    @handle_exceptions
    def func_raises_general_exception():
        raise Exception('general error occurred')

    response = func_raises_general_exception()

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {'error': 'general error occurred'}


def test_handle_exceptions_no_exception():
    @handle_exceptions
    def func_no_exception():
        return 'success'

    response = func_no_exception()

    assert response == 'success'


# ----------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_async_handle_exceptions_with_validation_error():
    @async_handle_exceptions
    async def func_raises_validation_error():
        raise ValidationError('validation error occurred')

    response = await func_raises_validation_error()

    expected_result = {'error': "[ErrorDetail(string='validation error occurred', code='invalid')]"}

    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    assert json.loads(response.content) == expected_result


@pytest.mark.asyncio
async def test_async_handle_exceptions_with_value_error():
    @async_handle_exceptions
    async def func_raises_value_error():
        raise ValueError('value error occurred')

    response = await func_raises_value_error()

    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    assert json.loads(response.content) == {'error': 'value error occurred'}


@pytest.mark.asyncio
async def test_async_handle_exceptions_with_general_exception():
    @async_handle_exceptions
    async def func_raises_general_exception():
        raise Exception('general error occurred')

    response = await func_raises_general_exception()

    assert isinstance(response, JsonResponse)
    assert response.status_code == 500
    assert json.loads(response.content) == {'error': 'general error occurred'}


@pytest.mark.asyncio
async def test_async_handle_exceptions_no_exception():
    @async_handle_exceptions
    async def func_no_exception():
        return 'success'

    response = await func_no_exception()

    assert response == 'success'


@pytest.mark.asyncio
async def test_async_handle_exceptions_with_page_not_an_integer():
    @async_handle_exceptions
    async def func_raises_page_not_an_integer():
        raise PageNotAnInteger('Page is not an integer')

    response = await func_raises_page_not_an_integer()

    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    assert json.loads(response.content) == {'error': 'Function does not support page argument'}


@pytest.mark.asyncio
async def test_async_handle_exceptions_with_empty_page():
    @async_handle_exceptions
    async def func_raises_empty_page():
        raise EmptyPage('This page is empty')

    response = await func_raises_empty_page()

    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data == {
        'items': [],
        'total': 0,
        'num_pages': 0,
        'current_page': 1
    }


@pytest.mark.asyncio
async def test_retry_with_page_one():
    async def func_page_one(page=None):
        assert page == 1
        return JsonResponse({'success': 'Page set to 1'}, status=200)

    response = await retry_with_page_one(func_page_one)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data == {'success': 'Page set to 1'}


@pytest.mark.asyncio
async def test_async_handle_exceptions_with_general_exception_during_pagination():
    @async_handle_exceptions
    async def func_raises_general_exception(*args, **kwargs):
        raise Exception

    response = await retry_with_page_one(func_raises_general_exception)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 500
    assert json.loads(response.content) == {'error': ''}
