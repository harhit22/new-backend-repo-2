import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from LabelCarftProjectSetup.models import Project


def list_dataset_files(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    dataset_path = f'static/media/datasets/{project_id}/'
    already_labeled_dataset = f'static/media/projects/annotated/{project_id}/images'

    if not os.path.exists(dataset_path):
        return JsonResponse({'success': False, 'error': 'Dataset not found'})

    # Get a list of image files in the already labeled dataset
    labeled_images = set()
    for root, dirs, files in os.walk(already_labeled_dataset):
        for file in files:

            labeled_images.add(file)

    # List all files in the dataset directory that do not have the same name in the already labeled dataset
    file_list = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            print(file)
            if file not in labeled_images:
                file_list.append(os.path.join(root, file).replace('static/', ''))

    return JsonResponse({'success': True, 'files': file_list})


from django.shortcuts import render

# Create your views here.
