from rest_framework import serializers

from cultural_places.models import CulturalPlace, UserPlacePreference


class CulturalPlaceSerializer(serializers.ModelSerializer):

    def validate(self, data):
        return data

    class Meta:
        model = CulturalPlace
        fields = (
            'id', 'name', 'description', 'address', 'opening_hours', 'image', 'created_at', 'updated_at', 'created_by',
            'updated_by')
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']


class UserPlacePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlacePreference
        fields = ['id', 'user', 'place', 'rating']
        read_only_fields = ['user']
