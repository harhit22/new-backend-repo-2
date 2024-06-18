from django.contrib import admin
import os

# Register your models here.
from .models import Image, Label


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id','original_image', 'image_name', 'project', 'category', 'image_file')

    def image_name(self, obj):
        return os.path.splitext(os.path.basename(obj.image_file.path))[0]

    image_name.short_description = 'Image'




class LabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_id', 'image', 'label', 'x', 'y', 'width', 'height', 'updated_at')


admin.site.register(Image, ImageAdmin)
admin.site.register(Label, LabelAdmin)
