from django.db import models
from LabelCarftProjectSetup.models import Project, ProjectCategory
from StoreLabelData.models import Image
import os
from django.contrib.auth.models import User


def upload_to(instance, filename):
    category_name = instance.category.category if instance.category else 'unknown'
    return f'projects/annotated/{instance.project.id}/images/{category_name}/{filename}'


class CategoryImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='category_images')
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, related_name='category_images', null=True,
                                 blank=True)
    firebase_url = models.URLField(max_length=500, blank=True, null=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='category_label_images')
    image_width = models.FloatField(blank=True, null=True, default=640)
    image_height = models.FloatField(blank=True, null=True, default=640)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='uploaded_labeled_images')

    def __str__(self):
        return f'{self.firebase_url}'


class ImageLabel(models.Model):
    category_image = models.ForeignKey(CategoryImage, on_delete=models.CASCADE, related_name='category_image_labels')
    label_id = models.CharField(max_length=100, unique=False)
    label = models.CharField(max_length=100)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Label: {self.label} for Image: {self.category_image}'
