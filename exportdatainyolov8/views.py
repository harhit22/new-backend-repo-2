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
import mimetypes
from django.http import HttpResponse
import traceback


def read_in_chunks(file_path, chunk_size=1024):
    """Generator to read a file in chunks."""
    with open(file_path, 'rb') as f:
        print(chunk)
        while chunk := f.read(chunk_size):
            yield chunk


def get_range_header(range_header, file_size):
    """
    Parse the Range header from the request to determine the start and end bytes.
    """
    if not range_header:
        return 0, file_size - 1

    range_value = range_header.strip().replace("bytes=", "")
    start, end = range_value.split("-")

    start = int(start) if start else 0
    end = int(end) if end else file_size - 1

    return start, end




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
        print(is_blur, "isblut")

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

        if result.ready():
            task_result = result.result
            if 'success' in task_result:
                file_path = os.path.join(settings.BASE_DIR, 'dataset', 'yolo_dataset.zip')
                if not os.path.exists(file_path):
                    return JsonResponse({'error': 'File not found'}, status=404)

                # Handle range requests
                file_size = os.path.getsize(file_path)
                range_header = request.headers.get("Range")
                start, end = get_range_header(range_header, file_size)

                chunk_size = end - start + 1
                response = HttpResponse(
                    open(file_path, 'rb').read()[start:end + 1],
                    status=206,
                    content_type=mimetypes.guess_type(file_path)[0] or "application/octet-stream"
                )
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Accept-Ranges'] = 'bytes'
                response['Content-Length'] = chunk_size
                response['Content-Disposition'] = 'attachment; filename="yolo_dataset.zip"'
                return response
            else:
                return JsonResponse({'error': 'Dataset generation failed'}, status=500)
        else:
            # Progress handling logic remains unchanged
            progress = result.info  # This contains the `processed` and `total` values
            processed = progress.get('processed', 0)
            percent = int(progress.get('percent', 0))
            total = progress.get('total', 0)
            if percent > 99:
                percent = 99
            return JsonResponse({
                'status': 'In progress',
                'processed': processed,
                'percent': percent,
                'total': total
            }, status=202)
