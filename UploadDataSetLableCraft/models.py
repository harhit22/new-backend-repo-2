from django.db import models
from LabelCarftProjectSetup.models import Project


class OriginalImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.filename}'

