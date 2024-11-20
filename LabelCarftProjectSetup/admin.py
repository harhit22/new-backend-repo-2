from django.contrib import admin
from .models import Project, Material, Grade, Condition, Toxicity, WasteType, ProjectCategory, ProjectInvitation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_by', 'created_at')
    filter_horizontal = ('members',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(Toxicity)
class ToxicityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(WasteType)
class WasteTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('project', 'category')
    search_fields = ('project__name', 'category')


@admin.register(ProjectInvitation)
class ProjectInvitationAdmin(admin.ModelAdmin):
    list_display = ('project', 'email', 'token', 'created_at', 'accepted', 'registered_user')
    search_fields = ('project__name', 'email', 'token')
    list_filter = ('accepted', 'created_at')
    raw_id_fields = ('project', 'registered_user')
