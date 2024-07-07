import pytest
from unittest.mock import Mock
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from user_profile.exceptions import handle_exceptions


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
    # Crear una función mock que lanza una ValueError
    @handle_exceptions
    def func_raises_value_error():
        raise ValueError('value error occurred')

    response = func_raises_value_error()

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'error': 'value error occurred'}


def test_handle_exceptions_with_general_exception():
    # Crear una función mock que lanza una excepción genérica
    @handle_exceptions
    def func_raises_general_exception():
        raise Exception('general error occurred')

    response = func_raises_general_exception()

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {'error': 'general error occurred'}


def test_handle_exceptions_no_exception():
    # Crear una función mock que no lanza ninguna excepción
    @handle_exceptions
    def func_no_exception():
        return 'success'

    response = func_no_exception()

    assert response == 'success'
