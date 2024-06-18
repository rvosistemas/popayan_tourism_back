from django.contrib import admin

from utils.mixin import EntityAdminMixin

from .models import ActivityCategory, LeisureActivity, UserActivityPreference

@admin.register(ActivityCategory)
class ActivityCategoryAdmin(EntityAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(LeisureActivity)
class LeisureActivityAdmin(EntityAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "image",
        "category",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(UserActivityPreference)
class UserActivityPreferenceAdmin(EntityAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "activity",
        "rating",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "activity__name")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
