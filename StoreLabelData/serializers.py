from rest_framework import serializers
from .models import Project, Image, Label, CategoryImageStatus
from cinx_backend.firebase import storage


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['image', 'label', 'x', 'y', 'width', 'height']


class ImageSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    image_file = serializers.ImageField(write_only=True)

    class Meta:
        model = Image
        fields = ['id', 'project', 'original_image', 'firebase_url', 'image_file', 'uploaded_at', 'uploaded_by']

    def create(self, validated_data):
        image_file = validated_data.pop('image_file')
        project = validated_data['project']
        filename = image_file.name

        # Upload the image to Firebase Storage
        blob = storage.bucket().blob(f'projects/{project.id}/annotated_images/{filename}')
        blob.upload_from_file(image_file)
        firebase_url = blob.public_url
        blob.make_public()

        # Create the Image instance
        validated_data['firebase_url'] = firebase_url
        image = Image.objects.create(**validated_data)

        return image


class ImageWithLabelsSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Image
        fields = ['id', 'project', 'category', 'image_file', 'uploaded_at', 'labels']


class CategoryImageStatusSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = CategoryImageStatus
        fields = ['id', 'category', 'image', 'assigned_to', 'status']

