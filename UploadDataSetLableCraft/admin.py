from django.contrib import admin
from .models import OriginalImage


class OriginalImageAdmin(admin.ModelAdmin):
    list_display = ('id', "project", "filename", "firebase_url", "assigned_to", "assigned_at", "completed", "status")
    list_filter = ("project", "assigned_to", "completed", "status")
    search_fields = ("filename", "firebase_url")


admin.site.register(OriginalImage, OriginalImageAdmin)
