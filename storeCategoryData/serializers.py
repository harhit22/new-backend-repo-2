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

        # Upload the image to Firebase Storage
        blob = storage.bucket().blob(f'projects/{project.id}/annotated_images/{category_name}/{filename}')
        blob.upload_from_file(image_file)
        firebase_url = blob.public_url
        blob.make_public()

        # Create the CategoryImage instance
        validated_data['firebase_url'] = firebase_url
        category_image = CategoryImage.objects.create(**validated_data)

        return category_image


class ImageLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageLabel
        fields = '__all__'
