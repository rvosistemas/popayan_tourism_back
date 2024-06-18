# Generated by Django 5.0.2 on 2024-06-14 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(default='2001-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
