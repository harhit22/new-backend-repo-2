from django.contrib import admin
from .models import ImageAssignment


class ImageAssignmentAdmin(admin.ModelAdmin):
    list_display = ('project', 'image', 'assigned_to', 'assigned_at', 'completed')
    list_filter = ('project', 'assigned_to', 'completed')


admin.site.register(ImageAssignment, ImageAssignmentAdmin)
