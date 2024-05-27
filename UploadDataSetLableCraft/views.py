from LabelCarftProjectSetup.models import Project
from django.http import JsonResponse
import os
import zipfile
from django.shortcuts import get_object_or_404


def upload_dataset(request, project_id):
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
                # Extract all files directly into the target directory
                for member in zip_ref.namelist():
                    # Remove any leading directory components
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
                # Extract all files directly into the target directory
                for member in zip_ref.namelist():
                    # Remove any leading directory components
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
