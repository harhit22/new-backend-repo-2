from LabelCarftProjectSetup.models import Project
from django.contrib.auth.models import User
from django.db import models
from LabelCarftProjectSetup.models import Project
from django.contrib.auth.models import User


class OriginalImage(models.Model):
    STATUS_CHOICES = [
        ('unassigned', 'Unassigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unassigned')

    def __str__(self):
        return f'{self.filename}'
