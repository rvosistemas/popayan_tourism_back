# serializers.py
from datetime import date
from rest_framework import serializers
from .models import User
from utils.logger import app_logger


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data) -> dict:
        username = data.get('username')
        email = data.get('email')
        date_of_birth = data.get('date_of_birth')

        today = date.today()
        difference_day_month = ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        age = today.year - date_of_birth.year - difference_day_month

        errors = {}

        if age < 12:
            app_logger.error("You must be at least 12 years old")
            errors['date_of_birth'] = 'You must be at least 12 years old'
        elif age > 100:
            app_logger.error("Age cannot be more than 100 years")
            errors['date_of_birth'] = 'Age cannot be more than 100 years'

        if User.objects.filter(username=username).exists():
            app_logger.error("Username already exists")
            errors['username'] = 'Username already exists'
        if User.objects.filter(email=email).exists():
            app_logger.error("Email already exists")
            errors['email'] = 'Email already exists'

        if errors:
            app_logger.error(f"Some errors occurred: {errors}")
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        app_logger.info("User created")
        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'date_of_birth')
