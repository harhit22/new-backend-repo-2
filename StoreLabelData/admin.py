from django.contrib import admin
import os

# Register your models here.
from .models import Image, Label


class LabelAdmin(admin.ModelAdmin):
    list_display = ('label', 'image_name', 'x', 'y', 'width', 'height', 'updated_at')

    def image_name(self, obj):
        return os.path.splitext(os.path.basename(obj.image.image_file.path))[0]

    image_name.admin_order_field = 'image__image_file'

admin.site.register(Image)
admin.site.register(Label, LabelAdmin)
