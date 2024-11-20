# models.py
from django.db import models
from django.contrib.auth.models import User


def user_photo_path(instance, filename):
    # Construct the file path for the user's photo
    return f'user_photos/{instance.user.id}/{filename}'


class UserPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=user_photo_path)

