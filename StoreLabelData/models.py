from django.db import models
from LabelCarftProjectSetup.models import Project, ProjectCategory
import os
from UploadDataSetLableCraft.models import OriginalImage
from django.contrib.auth.models import User


def upload_to(instance, filename):
    return f'projects/annotated/{instance.project.id}/images/{filename}'


class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')

    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE, related_name='OriginalImage')
    image_file = models.ImageField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='uploaded_images')

    def __str__(self):
        return f'{ os.path.splitext(os.path.basename(self.image_file.path))[0]}'


class Label(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='labels')
    label = models.CharField(max_length=100, blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.label} { os.path.splitext(os.path.basename(self.image.image_file.path))[0]}'


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
