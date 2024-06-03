from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string
import os


def dataset_upload_path(instance, filename):
    return f"datasets/{instance.id}/{filename}"


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, related_name='created_projects', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dataset = models.FileField(upload_to=dataset_upload_path, null=True, blank=True)

    def __str__(self):
        return self.name


class ProjectInvitation(models.Model):
    project = models.ForeignKey(Project, related_name='invitations', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=50, unique=True, default=get_random_string(length=20))
    created_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)
    registered_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'Invitation to {self.email} for project {self.project.name}'
