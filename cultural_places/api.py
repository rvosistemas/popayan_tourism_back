# cultural_places/api.py
from uuid import UUID

from django.core.paginator import Paginator
from django.http import JsonResponse
from ninja import NinjaAPI
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404

from cultural_places.models import CulturalPlace, UserPlacePreference
from cultural_places.serializers import CulturalPlaceSerializer, UserPlacePreferenceSerializer
from user_profile.auth import JWTAuth
from utils.logger import app_logger
from .pydantic_serializers import (
    SuccessCreateResponse, ErrorCreateResponse, CulturalPlaceSchema,
    SuccessEditResponse, ErrorEditResponse, SuccessDeactivateResponse, ErrorDeactivateResponse, SuccessDeleteResponse,
    ErrorDeleteResponse, UserPlacePreferenceOutputSchema, UserPlacePreferenceInputSchema
)
from utils.exceptions import async_handle_exceptions

api = NinjaAPI()


@api.get("", response=dict, auth=JWTAuth())
@async_handle_exceptions(empty_list_key='cultural_places')
async def get_cultural_places(request, page: int = 1, per_page: int = 10) -> dict:
    user = request.auth
    superuser = True if user.is_superuser else False
    if superuser:
        cultural_places_qs = await sync_to_async(list)(CulturalPlace.objects.all())
    else:
        cultural_places_qs = await sync_to_async(list)(CulturalPlace.objects.filter(active=True))

    paginator = await sync_to_async(Paginator)(cultural_places_qs, per_page)
    cultural_places = await sync_to_async(paginator.page)(page)

    serialized_data = [CulturalPlaceSchema.from_orm(place, is_admin=superuser).dict() for place in cultural_places]
    app_logger.info("Cultural places retrieved with pagination")

    response = {
        "cultural_places": serialized_data,
        "total": paginator.count,
        "num_pages": paginator.num_pages,
        "current_page": cultural_places.number if cultural_places else 1,
    }

    return response


@api.get("/cultural_place/{place_id}", response={200: CulturalPlaceSchema, 404: str}, auth=JWTAuth())
@async_handle_exceptions
async def get_cultural_place(request, place_id: UUID) -> CulturalPlaceSchema:
    user = request.auth
    superuser = True if user.is_superuser else False
    if superuser:
        cultural_place = await sync_to_async(CulturalPlace.objects.get)(id=place_id)
    else:
        cultural_place = await sync_to_async(CulturalPlace.objects.get)(id=place_id, active=True)
    app_logger.info(f"Cultural place {place_id} retrieved")
    return CulturalPlaceSchema.from_orm(cultural_place, is_admin=superuser)


@api.post("/cultural_place/", response={201: SuccessCreateResponse, 400: ErrorCreateResponse}, auth=JWTAuth())
@async_handle_exceptions
async def create_cultural_place(request, payload: CulturalPlaceSchema) -> JsonResponse:
    serializer = CulturalPlaceSerializer(data=payload.dict())
    if await sync_to_async(serializer.is_valid)():
        cultural_place = await sync_to_async(serializer.save)(created_by=request.user, updated_by=request.user)
        app_logger.info(f"Cultural place created by user {request.user.id}")
        place_data = CulturalPlaceSchema.from_orm(cultural_place).dict()
        return JsonResponse({"detail": "Cultural place created", "place": place_data}, status=201)


@api.put("/cultural_place/{place_id}", response={200: SuccessEditResponse, 400: ErrorEditResponse}, auth=JWTAuth())
@async_handle_exceptions
async def update_cultural_place(request, place_id: UUID, payload: CulturalPlaceSchema) -> JsonResponse:
    user = request.auth
    cultural_place = await sync_to_async(get_object_or_404)(CulturalPlace.objects.filter(active=True), id=place_id)

    if not user.is_superuser and cultural_place.created_by != user:
        return JsonResponse({"error": "You do not have permission to update this cultural place"}, status=403)

    serializer = CulturalPlaceSerializer(cultural_place, data=payload.dict(), partial=True)
    if await sync_to_async(serializer.is_valid)():
        updated_place = await sync_to_async(serializer.save)(updated_by=user)
        app_logger.info(f"Cultural place updated by user {user.id}")
        place_data = CulturalPlaceSchema.from_orm(updated_place).dict()
        msg = f"Cultural place {place_id} updated"
        return JsonResponse({"detail": msg, "place": place_data}, status=200)


@api.delete("/cultural_place/{place_id}", response={204: SuccessDeleteResponse, 404: ErrorDeleteResponse},
            auth=JWTAuth())
@async_handle_exceptions
async def delete_cultural_place(request, place_id: UUID) -> JsonResponse:
    user = request.auth

    if not user.is_superuser:
        return JsonResponse({"error": "You do not have permission to delete this cultural place"}, status=403)

    cultural_place = await sync_to_async(get_object_or_404)(CulturalPlace.objects.filter(active=True), id=place_id)
    await sync_to_async(cultural_place.delete)()
    msg = f"Cultural place {place_id} deleted"
    app_logger.info(msg)
    return JsonResponse({"detail": msg}, status=204)


@api.patch("/cultural_place/{place_id}/deactivate",
           response={200: SuccessDeactivateResponse, 404: ErrorDeactivateResponse}, auth=JWTAuth())
@async_handle_exceptions
async def deactivate_cultural_place(request, place_id: UUID) -> JsonResponse:
    user = request.auth

    if not user.is_superuser:
        return JsonResponse({"error": "You do not have permission to deactivate this cultural place"}, status=403)

    cultural_place = await sync_to_async(get_object_or_404)(CulturalPlace.objects.filter(active=True), id=place_id)
    if not cultural_place.active:
        return JsonResponse({"error": "Cultural place is already deactivated"}, status=400)

    cultural_place.active = False
    cultural_place.updated_by = user
    await sync_to_async(cultural_place.save)()
    msg = f"Cultural place {place_id} deactivated"
    app_logger.info(msg)
    place_data = CulturalPlaceSchema.from_orm(cultural_place).dict()
    return JsonResponse({"detail": msg, "place": place_data}, status=200)


@api.post("/user_place_preference/",
          response={201: UserPlacePreferenceOutputSchema, 200: UserPlacePreferenceOutputSchema, 400: str},
          auth=JWTAuth())
@async_handle_exceptions
async def create_user_place_preference(request, payload: UserPlacePreferenceInputSchema) -> JsonResponse:
    user = request.auth

    preference, created = await sync_to_async(UserPlacePreference.objects.update_or_create)(
        user=user,
        place_id=payload.place,
        defaults={'rating': payload.rating}
    )

    preference_data = UserPlacePreferenceOutputSchema.from_orm(preference).dict()
    msg = "User place preference created" if created else "User place preference updated"
    app_logger.info(f"{msg} by user {user.id}")
    return JsonResponse(preference_data, status=201 if created else 200)


@api.get("/user_place_preferences/", response={200: list[UserPlacePreferenceOutputSchema]}, auth=JWTAuth())
@async_handle_exceptions
async def get_user_place_preferences(request) -> list:
    user = request.auth

    preferences = await sync_to_async(list)(UserPlacePreference.objects.filter(user=user))
    serialized_data = [UserPlacePreferenceOutputSchema.from_orm(pref).dict() for pref in preferences]
    app_logger.info(f"Retrieved user place preferences for user {user.id}")
    return serialized_data
