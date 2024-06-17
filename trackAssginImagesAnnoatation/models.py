from django.db import models
from django.contrib.auth.models import User
from LabelCarftProjectSetup.models import Project
from UploadDataSetLableCraft.models import OriginalImage


class ImageAssignment(models.Model):
    STATUS_CHOICES = [
        ('unassigned', 'Unassigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unassigned')

    class Meta:
        unique_together = ('project', 'image')

    def __str__(self):
        return f'{self.image.filename} - {self.assigned_to.username if self.assigned_to else "Unassigned"}'

