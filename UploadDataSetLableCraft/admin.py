from django.contrib import admin
from .models import OriginalImage


class OriginalImageAdmin(admin.ModelAdmin):
    fields = ["id", "project", "filename", "path"]
    list_display = ("id", "project", "filename", "path")

admin.site.register(OriginalImage)