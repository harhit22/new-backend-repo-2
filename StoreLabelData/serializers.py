from rest_framework import serializers
from .models import Project, Image, Label, CategoryImageStatus
from cinx_backend.firebase import storage


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['image', 'label', 'x', 'y', 'width', 'height']


class ImageSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    image_file = serializers.CharField(write_only=True)

    class Meta:
        model = Image
        fields = ['id', 'project', 'original_image', 'firebase_url', 'image_file','uploaded_at', 'uploaded_by', "image_width", "image_height"]

    def create(self, validated_data):
        print(validated_data)
        image_file = validated_data.pop('image_file')
        project = validated_data['project']
        filename = image_file

        # Check for the image in the root folder
        root_blob_path = f'projects/{project.id}/{filename}'
        root_blob = storage.bucket().blob(root_blob_path)

        if root_blob.exists():
            # Image already exists in the root folder, reuse its URL
            firebase_url = root_blob.public_url
        else:
            # Upload the image to the 'annotated_images' folder only if it doesn't exist
            blob_path = f'projects/{project.id}/annotated_images/{filename}'
            blob = storage.bucket().blob(blob_path)
            print("here")
            print(type(image_file))
            print("here")
            blob.upload_from_file(image_file)
            blob.make_public()
            firebase_url = blob.public_url

        # Create the Image instance with the Firebase URL
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

