from django.db import models
from LabelCarftProjectSetup.models import Project, ProjectCategory
import os
from UploadDataSetLableCraft.models import OriginalImage
from django.contrib.auth.models import User
import uuid
from datetime import datetime

def upload_to(instance, filename):
    return f'projects/annotated/{instance.project.id}/images/{filename}'


class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')

    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE, related_name='OriginalImage')
    firebase_url = models.URLField(max_length=500, blank=True, null=True)
    image_width = models.FloatField(blank=True, null=True, default=540)
    image_height = models.FloatField(blank=True, null=True, default=540)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='uploaded_images')

    def __str__(self):
        return f'{self.firebase_url}'


class Label(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='labels')
    label = models.CharField(max_length=100, blank=True, null=True)
    label_id = models.CharField(max_length=100, unique=True, editable=False)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate label_id if it doesn't exist
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if not self.label_id:
            self.label_id = str(uuid.uuid4()) + str(timestamp)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.label} '


class CategoryImageStatus(models.Model):
    STATUS_CHOICES = [
        ('unlabeled', 'Unlabeled'),
        ('labeled', 'Labeled'),
        ('in_progress', 'In Progress'),
    ]
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='image_statuses')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='category_statuses')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unlabeled')

    def __str__(self):
        return f'{self.image} - {self.category} - {self.status}'

