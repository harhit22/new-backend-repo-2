from django.contrib import admin
from .models import CategoryImage, ImageLabel

from django.db.models import Count

class DuplicateImageFilter(admin.SimpleListFilter):
    title = 'Duplicate Images'  # Title of the filter
    parameter_name = 'duplicate_images'  # Parameter name in the URL

    def lookups(self, request, model_admin):
        # Providing options for filtering
        return (
            ('has_duplicates', 'Has Duplicates'),
            ('no_duplicates', 'No Duplicates'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'has_duplicates':
            # Filter to show only the images with duplicates
            return queryset.filter(image__in=CategoryImage.objects.values('image')
                                   .annotate(image_count=Count('image'))
                                   .filter(image_count__gt=1)
                                   .values('image'))
        if self.value() == 'no_duplicates':
            # Filter to show only the images with no duplicates
            return queryset.filter(image__in=CategoryImage.objects.values('image')
                                   .annotate(image_count=Count('image'))
                                   .filter(image_count=1)
                                   .values('image'))
        return queryset

class CategoryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'category', 'image', 'image_width', 'image_height', 'updated_at', 'uploaded_by']
    list_filter = ['project', 'image', 'uploaded_by', 'updated_at', DuplicateImageFilter]  # Add the custom filter here
    search_fields = ['category']  # Add fields for search


class ImageLabelAdmin(admin.ModelAdmin):
    list_display = ['id','label_id', 'category_image', 'label', 'x', 'y', 'width', 'height']


admin.site.register(CategoryImage, CategoryImageAdmin)
admin.site.register(ImageLabel, ImageLabelAdmin)
