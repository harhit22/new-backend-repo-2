from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from LabelCarftProjectSetup.models import Project
from UploadDataSetLableCraft.models import OriginalImage
from .models import ImageAssignment

@login_required
def assign_image(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user = request.user

    # Find an unassigned image
    unassigned_image = OriginalImage.objects.filter(
        project=project
    ).exclude(
        id__in=ImageAssignment.objects.filter(project=project).values_list('image_id', flat=True)
    ).first()

    if not unassigned_image:
        return JsonResponse({'success': False, 'error': 'No unassigned images found'})

    # Assign the image to the user
    assignment, created = ImageAssignment.objects.get_or_create(
        project=project,
        image=unassigned_image,
        defaults={'assigned_to': user, 'assigned_at': timezone.now(), 'completed': False}
    )

    if not created and assignment.assigned_to != user:
        return JsonResponse({'success': False, 'error': 'Image is already assigned to another user'})

    return JsonResponse({'success': True, 'file': unassigned_image.path, 'image_id': unassigned_image.id})


@login_required
def complete_image_labeling(request, project_id, image_id):
    project = get_object_or_404(Project, id=project_id)
    user = request.user

    try:
        assignment = ImageAssignment.objects.get(
            project=project, image_id=image_id, assigned_to=user, completed=False
        )
        assignment.completed = True
        assignment.save()
        return JsonResponse({'success': True})
    except ImageAssignment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Assignment not found or already completed'})

