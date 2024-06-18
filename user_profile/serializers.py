# En tu archivo serializers.py
from datetime import date
from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        date_of_birth = data.get('date_of_birth')

        today = date.today()
        difference_day_month = ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        age = today.year - date_of_birth.year - difference_day_month

        if age < 12:
            raise serializers.ValidationError('You must be at least 12 years old')
        if age > 100:
            raise serializers.ValidationError('Age cannot be more than 100 years')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'date_of_birth')
