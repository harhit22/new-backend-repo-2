# admin.py
from django.contrib import admin
from .models import ImageAssignment


class ImageAssignmentAdmin(admin.ModelAdmin):
    fields = ['project', 'image', 'assigned_to', 'assigned_at', 'completed', 'status']
    list_display = ('id', 'project', 'image', 'assigned_to', 'assigned_at', 'completed', 'status')
    list_filter = ('project', 'assigned_to', 'completed', 'status')
    search_fields = ('project__name', 'image__filename', 'assigned_to__username')
    readonly_fields = ('assigned_at',)


admin.site.register(ImageAssignment, ImageAssignmentAdmin)

