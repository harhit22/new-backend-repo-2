from LabelCarftProjectSetup.models import Project
from .models import OriginalImage
from django.http import JsonResponse
import os
import zipfile
from django.shortcuts import get_object_or_404
from .models import OriginalImage
import shutil


def upload_dataset(request, project_id):
    if request.method == 'POST' and request.FILES.get('dataset'):
        project = get_object_or_404(Project, id=project_id)
        dataset = request.FILES['dataset']

        temp_dir = 'temp_extract_dir'
        os.makedirs(temp_dir, exist_ok=True)

        try:
            zip_path = os.path.join(temp_dir, 'uploaded_dataset.zip')
            with open(zip_path, 'wb+') as destination:
                for chunk in dataset.chunks():
                    destination.write(chunk)

            extract_path = f'static/media/datasets/{project_id}/'
            os.makedirs(extract_path, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            os.remove(zip_path)
            shutil.rmtree(temp_dir)

            return JsonResponse({'success': True})
        except zipfile.BadZipFile:
            os.remove(zip_path)
            shutil.rmtree(temp_dir)
            return JsonResponse({'success': False, 'error': 'Invalid zip file'})
        except Exception as e:
            shutil.rmtree(temp_dir)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No file uploaded'})


def upload_dataset_extend(request, project_id):
    if request.method == 'POST' and request.FILES.get('dataset'):
        project = get_object_or_404(Project, id=project_id)
        dataset = request.FILES['dataset']

        # Save the uploaded zip file
        zip_path = 'uploaded_dataset.zip'
        with open(zip_path, 'wb+') as destination:
            for chunk in dataset.chunks():
                destination.write(chunk)

        # Define the extraction path
        extract_path = f'static/media/datasets/{project_id}/'

        # Ensure the extraction path exists
        os.makedirs(extract_path, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    member_path = os.path.join(extract_path, os.path.basename(member))
                    if not os.path.isdir(member_path):
                        with open(member_path, 'wb') as output_file:
                            with zip_ref.open(member) as source_file:
                                output_file.write(source_file.read())

            # Remove the uploaded zip file
            os.remove(zip_path)

            return JsonResponse({'success': True})
        except zipfile.BadZipFile:
            os.remove(zip_path)
            return JsonResponse({'success': False, 'error': 'Invalid zip file'})

    return JsonResponse({'success': False, 'error': 'No file uploaded'})
