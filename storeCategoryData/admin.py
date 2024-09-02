from django.contrib import admin
from .models import CategoryImage, ImageLabel


class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'category', 'image_file', 'image', 'image_width', 'image_height', 'updated_at', 'uploaded_by']


class ImageLabelAdmin(admin.ModelAdmin):
    list_display = ['id',  'category_image', 'label', 'x', 'y', 'width', 'height']


admin.site.register(CategoryImage, CategoryImageAdmin)
admin.site.register(ImageLabel, ImageLabelAdmin)
