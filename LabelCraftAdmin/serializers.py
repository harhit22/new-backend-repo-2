from rest_framework import serializers
from UploadDataSetLableCraft.models import OriginalImage
from storeCategoryData.models import CategoryImage, ImageLabel
from StoreLabelData.models import Image, Label


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = ['id', 'filename', 'path', 'status', 'assigned_to', 'assigned_at', 'completed']


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
        fields = ['id', 'project', 'original_image', 'image_file', 'uploaded_at', 'uploaded_by', 'labels']


# -----------------------------------------------------------------------------------------------------
class ImageLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLabel
        fields = ['label', 'x', 'y', 'width', 'height']


class LabeledImageSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    labels = ImageLabelSerializer(many=True, source='category_image_labels')

    class Meta:
        model = CategoryImage
        fields = ['id', 'project', 'category', 'image_file', 'image_width', 'image_height', 'updated_at', 'uploaded_by',
                  'labels']
