from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import PageNotAnInteger, EmptyPage
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


def async_handle_exceptions(func=None, *, empty_list_key=None):
    """
    Decorador para manejar excepciones de forma asíncrona en las vistas de NinjaAPI.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                app_logger.error(f"Value error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=400)
            except ValidationError as e:
                app_logger.error(f"Validation error: {str(e)}")
                return JsonResponse({'error': str(e.detail)}, status=400)
            except ObjectDoesNotExist as e:
                app_logger.error(f"Object Does Not Exist: {str(e)}")
                return JsonResponse({'error': str(e)}, status=400)
            except (PageNotAnInteger, EmptyPage) as e:
                return await handle_pagination_exceptions(func, e, empty_list_key, *args, **kwargs)
            except Exception as e:
                app_logger.error(f"General Exception: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)

        return wrapper

    if func:
        return decorator(func)

    return decorator


async def handle_pagination_exceptions(func, exception, empty_list_key, *args, **kwargs):
    """
    Maneja las excepciones relacionadas con la paginación.
    """
    if isinstance(exception, PageNotAnInteger):
        app_logger.warning("Page not an integer, defaulting to page 1")
        return await retry_with_page_one(func, *args, **kwargs)

    if isinstance(exception, EmptyPage):
        app_logger.warning("Empty page, returning empty list")
        return JsonResponse({
            empty_list_key or 'items': [],
            'total': 0,
            'num_pages': 0,
            'current_page': 1
        }, status=200)


async def retry_with_page_one(func, *args, **kwargs):
    """
    Reintenta la función con la página configurada a 1.
    """
    try:
        kwargs['page'] = 1
        return await func(*args, **kwargs)
    except TypeError as e:
        app_logger.error(f"Failed to paginate to page 1: {str(e)}")
        return JsonResponse({'error': 'Function does not support page argument'}, status=400)
