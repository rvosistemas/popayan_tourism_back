import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from utils.models import Entity


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField()


class UserProfile(Entity):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="%(app_label)s_%(class)s_user")
    preferences = models.JSONField(default=dict, blank=True, null=True)
    activity_history = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"user: {self.user.username}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = "user_profile"
        managed = True
