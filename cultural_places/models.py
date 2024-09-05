import uuid

from django.db import models
from django.conf import settings

from utils.models import Entity
from .validators import validate_opening_hours


class CulturalPlace(Entity):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    address = models.CharField(max_length=255)
    opening_hours = models.JSONField(validators=[validate_opening_hours])
    image = models.ImageField(upload_to="cultural_places", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cultural Place"
        verbose_name_plural = "Cultural Places"
        db_table = "cultural_place"
        managed = True


class UserPlacePreference(Entity):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_user"
    )
    place = models.ForeignKey(CulturalPlace, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_place")
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"user: {self.user.username}, place: {self.place.name}, rating: {self.rating}"

    class Meta:
        verbose_name = "User Place Preference"
        verbose_name_plural = "User Place Preferences"
        db_table = "user_place_preference"
        managed = True
