from django.contrib import admin

from utils.mixin import EntityAdminMixin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(EntityAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "preferences",
        "activity_history",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
