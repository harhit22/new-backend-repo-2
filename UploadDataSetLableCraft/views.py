from LabelCarftProjectSetup.models import Project
from django.http import JsonResponse
import os
import zipfile


def upload_dataset(request, project_id):
    if request.method == 'POST' and request.FILES.get('dataset'):
        project = Project.objects.get(id=project_id)
        dataset = request.FILES['dataset']

        # Save the uploaded zip file
        with open('uploaded_dataset.zip', 'wb+') as destination:
            for chunk in dataset.chunks():
                destination.write(chunk)

        # Extract the contents of the zip file
        with zipfile.ZipFile('uploaded_dataset.zip', 'r') as zip_ref:
            zip_ref.extractall(f'static/media/datasets/{project_id}/')

        # Remove the uploaded zip file
        os.remove('uploaded_dataset.zip')

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'No file uploaded'})
