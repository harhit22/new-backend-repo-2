# serializers.py
from rest_framework import serializers
from .models import ImageAssignment



class ImageAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageAssignment
        fields = ['id', 'project', 'image', 'assigned_to', 'assigned_at', 'completed', 'status']
