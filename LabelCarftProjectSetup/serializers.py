from .models import Project, ProjectInvitation
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_by', 'members', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class ProjectInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvitation
        fields = ['id', 'project', 'email', 'token', 'created_at', 'accepted', 'registered_user']
        read_only_fields = ['token', 'created_at', 'accepted', 'registered_user']