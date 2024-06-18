import uuid

from django.db import models
from django.conf import settings

from utils.models import Entity


class ActivityCategory(Entity):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Activity Category"
        verbose_name_plural = "Activity Categories"
        db_table = "activity_category"
        managed = True


class LeisureActivity(Entity):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="leisure_activities", blank=True, null=True)
    category = models.ForeignKey(
        ActivityCategory, on_delete=models.CASCADE, related_name="activities"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Leisure Activity"
        verbose_name_plural = "Leisure Activities"
        db_table = "leisure_activity"
        managed = True


class UserActivityPreference(Entity):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_user")
    activity = models.ForeignKey(LeisureActivity, on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_activity")
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"user: {self.user.username}, activity: {self.activity.name}, rating: {self.rating}"

    class Meta:
        verbose_name = "User Activity Preference"
        verbose_name_plural = "User Activity Preferences"
        db_table = "user_activity_preference"
        managed = True
