from django.contrib import admin
import os

# Register your models here.
from .models import Image, Label, CategoryImageStatus
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter

class DuplicateLabelFilter(SimpleListFilter):
    title = 'Duplicate Labels'
    parameter_name = 'duplicate_labels'

    def lookups(self, request, model_admin):
        return [('duplicates', 'Duplicates')]

    def queryset(self, request, queryset):
        if self.value() == 'duplicates':
            # Find duplicate entries based on specified fields excluding 'id'
            duplicate_entries = (
                queryset.values('image_id', 'image', 'label', 'x', 'y', 'width', 'height')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .values_list('image_id', 'image', 'label', 'x', 'y', 'width', 'height')
            )
            # Filter queryset to only include duplicates
            filters = Q()
            for entry in duplicate_entries:
                filters |= Q(
                    image_id=entry[0],
                    image=entry[1],
                    label=entry[2],
                    x=entry[3],
                    y=entry[4],
                    width=entry[5],
                    height=entry[6],
                )
            return queryset.filter(filters)
        return queryset


class DuplicateFirebaseURLFilter(SimpleListFilter):
    title = 'Duplicate Firebase URLs'
    parameter_name = 'duplicate_firebase_url'

    def lookups(self, request, model_admin):
        return [('duplicates', 'Duplicates')]

    def queryset(self, request, queryset):
        if self.value() == 'duplicates':
            duplicate_urls = (
                queryset.values('firebase_url')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .values_list('firebase_url', flat=True)
            )
            return queryset.filter(firebase_url__in=duplicate_urls)
        return queryset

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_image', 'project', 'firebase_url', 'uploaded_by',  "image_width", "image_height")
    search_fields = ('firebase_url',)
    list_filter = (DuplicateFirebaseURLFilter,)

class LabelAdmin(admin.ModelAdmin):
    list_display = ('id','label_id', 'image_id', 'image', 'label', 'x', 'y', 'width', 'height', 'updated_at')
    list_filter = (DuplicateLabelFilter,)
    actions = ['remove_duplicates']

    def remove_duplicates(self, request, queryset):
        # Find duplicate entries
        duplicates = (
            queryset.values('image_id', 'image', 'label', 'x', 'y', 'width', 'height')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        deleted_count = 0
        for duplicate in duplicates:
            # Get all duplicates for the current group
            duplicate_group = queryset.filter(
                image_id=duplicate['image_id'],
                image=duplicate['image'],
                label=duplicate['label'],
                x=duplicate['x'],
                y=duplicate['y'],
                width=duplicate['width'],
                height=duplicate['height'],
            )

            # Keep one and delete the rest
            ids_to_delete = list(duplicate_group.values_list('id', flat=True))[1:]
            queryset.model.objects.filter(id__in=ids_to_delete).delete()
            deleted_count += len(ids_to_delete)

        self.message_user(request, f"{deleted_count} duplicate entries removed.")

    remove_duplicates.short_description = "Remove duplicates (keep one per group)"

class CategoryImageStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'category', "assigned_to", 'status')
    search_fields = ('image',)

admin.site.register(Image, ImageAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(CategoryImageStatus, CategoryImageStatusAdmin)

