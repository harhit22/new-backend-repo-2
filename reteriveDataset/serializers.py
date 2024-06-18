from rest_framework import serializers
from .models import OriginalImage

class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = ['id', 'project', 'filename', 'path', 'assigned_to', 'assigned_at', 'completed', 'status']
