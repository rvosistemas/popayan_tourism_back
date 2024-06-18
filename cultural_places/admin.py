from django.contrib import admin

from utils.mixin import EntityAdminMixin

from .models import CulturalPlace, UserPlacePreference


@admin.register(CulturalPlace)
class CulturalPlaceAdmin(EntityAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "address",
        "opening_hours",
        "image",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(UserPlacePreference)
class UserPlacePreferenceAdmin(EntityAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "place",
        "rating",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "place__name")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
