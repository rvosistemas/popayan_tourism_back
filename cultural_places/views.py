import json

from asgiref.sync import sync_to_async
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import JsonResponse
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cultural_places.models import CulturalPlace
from cultural_places.serializers import CulturalPlaceSerializer
from cultural_places.swagger import (
    get_cultural_places_swagger_params, get_cultural_place_swagger_params,
    post_cultural_place_swagger_params, put_cultural_place_swagger_params,
    delete_cultural_place_swagger_params
)
from user_profile.authentication import CustomJWTAuthentication
from utils.exceptions import async_handle_exceptions
from utils.logger import app_logger


class CulturalPlacesView(View):
    permission_classes = [IsAuthenticated]

    @async_handle_exceptions
    @swagger_auto_schema(**get_cultural_places_swagger_params)
    async def get(self, request) -> JsonResponse:
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)

        cultural_places_qs = CulturalPlace.objects.all()

        paginator = Paginator(cultural_places_qs, per_page)

        try:
            cultural_places = await sync_to_async(paginator.page)(page)
        except PageNotAnInteger:
            cultural_places = await sync_to_async(paginator.page)(1)
        except EmptyPage:
            cultural_places = []

        serializer = CulturalPlaceSerializer(cultural_places, many=True)
        app_logger.info("Cultural places retrieved with pagination")

        response = {
            "cultural_places": serializer.data,
            "total": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": cultural_places.number if cultural_places else 1,
        }
        return JsonResponse(response, status=200)


class CulturalPlaceView(View):
    permission_classes = [IsAuthenticated]

    @async_handle_exceptions
    @swagger_auto_schema(**get_cultural_place_swagger_params)
    async def get(self, request, id) -> JsonResponse:
        try:
            cultural_place = await sync_to_async(CulturalPlace.objects.get)(id=id)
        except CulturalPlace.DoesNotExist:
            app_logger.error(f"CulturalPlace with id {id} does not exist.")
            return JsonResponse({'error': f"CulturalPlace with id {id} does not exist."}, status=404)

        serializer = CulturalPlaceSerializer(cultural_place)
        app_logger.info("Cultural place retrieved")
        return JsonResponse(serializer.data, status=200)


class CreateCulturalPlaceView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    @async_handle_exceptions
    @swagger_auto_schema(**post_cultural_place_swagger_params)
    async def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        serializer = CulturalPlaceSerializer(data=data)

        is_valid = await sync_to_async(serializer.is_valid)(raise_exception=True)
        if is_valid:
            print("--------request.user --------")
            print(request.user)

            await sync_to_async(serializer.save)(created_by=request.user, updated_by=request.user)
            app_logger.info(f"Cultural place created by user {request.user.id}")

            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class EditCulturalPlaceView(View):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @async_handle_exceptions
    @swagger_auto_schema(**put_cultural_place_swagger_params)
    async def put(self, request, id) -> JsonResponse:
        data = json.loads(request.body.decode('utf-8'))
        cultural_place = await sync_to_async(CulturalPlace.objects.get)(id=id)

        serializer = CulturalPlaceSerializer(cultural_place, data=data)

        is_valid = await sync_to_async(serializer.is_valid)(raise_exception=True)
        if is_valid:
            await sync_to_async(serializer.save)(updated_by=request.user)
            app_logger.info(f"Cultural place updated by user {request.user.id}")
            return JsonResponse(serializer.data, status=200)
        else:
            return JsonResponse(serializer.errors, status=400)

    @async_handle_exceptions
    @swagger_auto_schema(**delete_cultural_place_swagger_params)
    async def delete(self, request, id) -> JsonResponse:
        cultural_place = await sync_to_async(CulturalPlace.objects.get)(id=id)
        deleted_by_user = request.user
        await sync_to_async(cultural_place.delete)()
        app_logger.info(f"Cultural place deleted by user {deleted_by_user.id}")

        return JsonResponse(status=204)
