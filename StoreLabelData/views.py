from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Image, Label
from .serializers import ImageSerializer, LabelSerializer
from rest_framework.views import APIView
import os
from django.http import JsonResponse
import json
from rest_framework.response import Response
from django.db import transaction
from rest_framework.exceptions import ValidationError
import threading
from rest_framework.decorators import api_view

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            with transaction.atomic():
                # Check for an existing image using locking
                existing_image = Image.objects.select_for_update().filter(
                    firebase_url=data.get('firebase_url'),
                    project=data.get('project')
                ).first()

                if existing_image:
                    # Return the existing image if found
                    serializer = self.get_serializer(existing_image)
                    return Response(serializer.data, status=status.HTTP_200_OK)

                # Validate and create a new image
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def label_update(request, label_id):
    try:
        label = Label.objects.get(label_id=label_id)
    except Label.DoesNotExist:
        return Response({"error": "Label not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LabelSerializer(label, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer

    def perform_create(self, serializer):
        label = serializer.save()  # Save the label
        return Response(
            LabelSerializer(label).data,  # Return the serialized label with label_id
            status=status.HTTP_201_CREATED
        )


def list_dataset_files(request, project_id):
    dataset_path = f'static/media/projects/annotated/{project_id}/'

    if not os.path.exists(dataset_path):
        return JsonResponse({'success': False, 'error': 'Dataset not found'})

    file_list = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
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
            data = json.loads(request.body)
            image_id = data.get('image_id')
            print(f"Image ID: {image_id}")
            if not image_id:
                raise ValueError("Image ID is required")

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


class DeleteLabelById(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print('i am hereeeeeee')
            print("Request body (raw):", request.body)  # Log raw request body
            print("Parsed data:", request.data)  # Log parsed data
            label_id = request.data.get('label_id')  # Expect label_id from the request body
            print(label_id)

            if not label_id:
                raise ValueError("Label ID is required")



            # Fetch the label by ID
            label_to_delete = Label.objects.filter(label_id=label_id).first()

            if not label_to_delete:
                return JsonResponse({"success": False, "message": "Label not found"}, status=404)

            # Delete the label
            label_to_delete.delete()

            return JsonResponse({"success": True, "message": f"Label with ID {label_id} deleted successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
