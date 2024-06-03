from rest_framework import serializers
from .models import Project, Image, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['image', 'label', 'x', 'y', 'width', 'height']


class ImageSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Image
        fields = ['id', 'project', 'image_file', 'uploaded_at']
