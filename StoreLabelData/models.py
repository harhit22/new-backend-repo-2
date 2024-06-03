from django.db import models
from LabelCarftProjectSetup.models import Project
import os


def upload_to(instance, filename):
    return f'projects/annotated/{instance.project.id}/images/{filename}'


class Image(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image_file = models.ImageField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{ os.path.splitext(os.path.basename(self.image_file.path))[0]}'

class Label(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='labels')
    label = models.CharField(max_length=100)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.label} { os.path.splitext(os.path.basename(self.image.image_file.path))[0]}'
