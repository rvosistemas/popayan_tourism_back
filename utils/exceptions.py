from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from utils.logger import app_logger


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            app_logger.error(f"Validation error: {str(e)}")
            return Response({'error': str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            app_logger.error(f"Value error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            app_logger.error(f"General Exception: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper


def async_handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            app_logger.error(f"Validation error: {str(e)}")
            return JsonResponse({'error': str(e.detail)}, status=400)
        except ValueError as e:
            app_logger.error(f"Value error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except TypeError as e:
            app_logger.error(f"Type error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except ObjectDoesNotExist as e:
            app_logger.error(f"Object does not exist: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except OverflowError as e:
            app_logger.error(f"Overflow error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            app_logger.error(f"General Exception: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return wrapper
