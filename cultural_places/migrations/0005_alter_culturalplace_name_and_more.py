# Generated by Django 5.0.2 on 2024-08-30 19:37

import cultural_places.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cultural_places', '0004_culturalplace_opening_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='culturalplace',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='culturalplace',
            name='opening_hours',
            field=models.JSONField(validators=[cultural_places.validators.validate_opening_hours]),
        ),
    ]
