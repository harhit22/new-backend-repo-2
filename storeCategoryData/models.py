from django.db import models
from LabelCarftProjectSetup.models import Project, ProjectCategory
from StoreLabelData.models import Image
import os


def upload_to(instance, filename):
    category_name = instance.category.category if instance.category else 'unknown'
    return f'projects/annotated/{instance.project.id}/images/{category_name}/{filename}'


class CategoryImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='category_images')
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, related_name='category_images', null=True,
                                 blank=True)
    image_file = models.ImageField(upload_to=upload_to)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='category_label_images')
    image_width = models.FloatField(blank=True, null=True, default=640)
    image_height = models.FloatField(blank=True, null=True, default=640)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{os.path.splitext(os.path.basename(self.image_file.path))[0]}'


class ImageLabel(models.Model):
    category_image = models.ForeignKey(CategoryImage, on_delete=models.CASCADE, related_name='category_image_labels')
    label = models.CharField(max_length=100)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Label: {self.label} for Image: {self.category_image}'

