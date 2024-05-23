from django.contrib import admin

# Register your models here.
from .models import Project, ProjectInvitation

admin.site.register(Project)
admin.site.register(ProjectInvitation)