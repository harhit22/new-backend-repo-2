from rest_framework import serializers
from .models import Project, CategoryImage, ImageLabel
from LabelCarftProjectSetup.models import ProjectCategory
from cinx_backend.firebase import storage


class CategoryImageSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=ProjectCategory.objects.all(), required=False)
    image_file = serializers.ImageField(write_only=True)

    class Meta:
        model = CategoryImage
        fields = ['id', 'project', 'category', 'firebase_url', 'image', 'image_width', 'image_height',
                  'updated_at', 'uploaded_by', 'image_file']

    def create(self, validated_data):
        image_file = validated_data.pop('image_file')
        project = validated_data['project']
        category_name = validated_data.get('category', None).category if validated_data.get('category') else 'unknown'
        filename = image_file.name

        # Check for the image in the root folder
        root_blob_path = f'projects/{project.id}/{filename}'
        root_blob = storage.bucket().blob(root_blob_path)

        if root_blob.exists():
            # Image already exists in the root folder, reuse its URL
            firebase_url = root_blob.public_url
        else:
            # Upload the image to Firebase Storage under the category-specific folder
            blob_path = f'projects/{project.id}/annotated_images/{category_name}/{filename}'
            blob = storage.bucket().blob(blob_path)
            blob.upload_from_file(image_file)
            blob.make_public()
            firebase_url = blob.public_url

        # Create the CategoryImage instance
        validated_data['firebase_url'] = firebase_url
        category_image = CategoryImage.objects.create(**validated_data)

        return category_image


class ImageLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLabel
        fields = '__all__'
