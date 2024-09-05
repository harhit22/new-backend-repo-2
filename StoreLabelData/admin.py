from django.contrib import admin
import os

# Register your models here.
from .models import Image, Label, CategoryImageStatus


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_image', 'project', 'firebase_url', 'uploaded_by')


class LabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_id', 'image', 'label', 'x', 'y', 'width', 'height', 'updated_at')


class CategoryImageStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'category', "assigned_to", 'status')


admin.site.register(Image, ImageAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(CategoryImageStatus, CategoryImageStatusAdmin)
