from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Image, Label
from .serializers import ImageSerializer, LabelSerializer, ImageSerializer
from rest_framework.views import APIView
import os
from django.http import JsonResponse
import json

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


def list_dataset_files(request, project_id):
    dataset_path = f'static/media/projects/annotated/{project_id}/'

    if not os.path.exists(dataset_path):
        return JsonResponse({'success': False, 'error': 'Dataset not found'})

    # List all files in the dataset directory
    file_list = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            # Extract the file name and append to file_list
            file_list.append(os.path.basename(file))

    return JsonResponse({'success': True, 'files': file_list})


def get_image_id(request):
    project_id = request.GET.get('project')
    image_name = request.GET.get('image_name')

    try:
        image = Image.objects.get(project_id=project_id, image_file__contains=image_name)
        return JsonResponse({'id': image.id})
    except Image.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)


class DeleteLabelsForImage(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # Parse JSON data from request body
            image_id = data.get('image_id')  # Retrieve image_id from parsed JSON data
            print(f"Image ID: {image_id}")
            if not image_id:
                raise ValueError("Image ID is required")

            # Ensure the image_id is converted to an integer
            image_id = int(image_id)

            # Debug the SQL query being executed
            labels_to_delete = Label.objects.filter(image__id=image_id)
            print(f"Labels to delete: {labels_to_delete.query}")

            # Check the results of the queryset
            if not labels_to_delete.exists():
                print(f"No labels found for image_id: {image_id}")
            else:
                print(f"Found labels for image_id: {image_id}")

            # Delete the labels
            deleted_count, _ = labels_to_delete.delete()

            return JsonResponse({"success": True, "message": f"{deleted_count} labels deleted successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


