from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from LabelCarftProjectSetup.models import Material, Toxicity, Condition, Grade, WasteType
from storeCategoryData.models import CategoryImage, ImageLabel
import yaml
import random
import requests
import os
from pathlib import Path
import zipfile
from django.http import FileResponse
from django.conf import settings
import json
from django.http import StreamingHttpResponse
from .tasks import generate_yolo_dataset
import time
from django.core.cache import cache 


def read_in_chunks(file_path, chunk_size=1024):
    """Generator to read a file in chunks."""
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            yield chunk




@method_decorator(csrf_exempt, name='dispatch')
class DatasetDownloadView(View):
    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        category_id = body.get('category_id')
        category_name = body.get('category_name')
        train_images_num = body.get('train_count')
        val_images_num = body.get('val_count')
        test_images_num = body.get('test_count')
        is_blur = body.get('blur_images')
        # Call Celery task for background processing
        result = generate_yolo_dataset.apply_async(
            args=[category_id, category_name, train_images_num, val_images_num, test_images_num, is_blur]
        )

        # Respond immediately with task ID
        return JsonResponse({'task_id': result.id}, status=202)



@method_decorator(csrf_exempt, name='dispatch')
class TotalImagesByCategoryView(View):
    def get(self, request, *args, **kwargs):
        # Get the category ID from the request
        category_id = request.GET.get('category_id')

        # Check if category_id is provided
        if not category_id:
            return JsonResponse({'error': 'category_id is required'}, status=400)

        # Get the total number of images for the given category ID
        total_images = CategoryImage.objects.filter(category_id=category_id).count()

        # Return the total number of images as JSON response
        return JsonResponse({'category_id': category_id, 'total_images': total_images})


@method_decorator(csrf_exempt, name='dispatch')
class TaskStatusView(View):
    def get(self, request, *args, **kwargs):
        task_id = request.GET.get('task_id')

        if not task_id:
            return JsonResponse({'error': 'task_id is required'}, status=400)

        # Check the task status
        result = generate_yolo_dataset.AsyncResult(task_id)
        print(result.ready())

        # Wait for a small amount of time to ensure the result is ready
        time.sleep(2)

        if result.ready():
            task_result = result.result
            print(task_result)
            if 'success' in task_result:
                # File path where the dataset is saved
                file_path = os.path.join(settings.BASE_DIR, 'dataset', 'yolo_dataset.zip')
                if os.path.exists(file_path):
                    response = FileResponse(open(file_path, 'rb'))
                    response['Content-Disposition'] = 'attachment; filename="dataset.zip"'
                    return response
            else:
                return JsonResponse({'error': 'Dataset generation failed'}, status=500)
        else:
            return JsonResponse({'status': 'In progress'}, status=202)
