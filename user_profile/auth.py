import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from utils.logger import app_logger
from .models import User
from ninja.security import HttpBearer


class JWTAuth(HttpBearer):
    async def authenticate(self, request, token):
        try:
            payload = await sync_to_async(jwt.decode)(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            user = await sync_to_async(User.objects.get)(id=user_id)
            app_logger.info(f"User authenticated: {user_id}")
            return user

        except jwt.ExpiredSignatureError:
            app_logger.error("Expired token")
            return None
        except jwt.InvalidTokenError:
            app_logger.error("Invalid token")
            return None
        except User.DoesNotExist:
            app_logger.error("User does not exist")
            return None
        except Exception as e:
            app_logger.error(f"Authentication error: {str(e)}")
            return None
