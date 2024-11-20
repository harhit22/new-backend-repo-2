from rest_framework import serializers
from UploadDataSetLableCraft.models import OriginalImage
from storeCategoryData.models import CategoryImage, ImageLabel
from StoreLabelData.models import Image, Label


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = ['id', 'filename', 'firebase_url', 'status', 'assigned_to', 'assigned_at', 'completed']


# -----------------------------------------------------------------------------------------------------
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label', 'x', 'y', 'width', 'height']


class AnnotatedImageSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    labels = LabelSerializer(many=True)

    class Meta:
        model = Image
        fields = ['id', 'project', 'original_image','firebase_url', 'uploaded_at', 'uploaded_by', 'labels', "image_width", "image_height"]


# -----------------------------------------------------------------------------------------------------
class ImageLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLabel
        fields = ['label', 'x', 'y', 'width', 'height']


class LabeledImageSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    labels = ImageLabelSerializer(many=True, source='category_image_labels')
    category_name = serializers.CharField(source='category', read_only=True)

    class Meta:
        model = CategoryImage
        fields = ['id', 'project', 'category', 'category_name', 'firebase_url', 'image_width', 'image_height', 'updated_at', 'uploaded_by', 'labels']

