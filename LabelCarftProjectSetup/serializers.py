from .models import Project, ProjectInvitation, ProjectCategory, Material, Grade, Condition, Toxicity, WasteType
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


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'category', 'color']


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'category', 'color']


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ['id', 'name', 'category', 'color']


class ToxicitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Toxicity
        fields = ['id', 'name', 'category', 'color']


class WasteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteType
        fields = ['id', 'name', 'category', 'color']


class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ['id', 'category']
