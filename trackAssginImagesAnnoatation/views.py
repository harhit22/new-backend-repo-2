# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from LabelCarftProjectSetup.models import Project
from .models import ImageAssignment
from .serializers import ImageAssignmentSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

class NextImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        user = request.user

        unassigned_image_assignment = ImageAssignment.objects.filter(
            project=project,
            status='unassigned'
        ).first()

        if unassigned_image_assignment:
            unassigned_image_assignment.assigned_to = user
            unassigned_image_assignment.status = 'in_progress'
            unassigned_image_assignment.save()

            serializer = ImageAssignmentSerializer(unassigned_image_assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'error': 'No unassigned images available'}, status=status.HTTP_404_NOT_FOUND)

class UpdateImageStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assignment_id, status):
        if status not in ['in_progress', 'completed']:
            return Response({'success': False, 'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        image_assignment = get_object_or_404(ImageAssignment, id=assignment_id)
        image_assignment.status = status

        if status == 'completed':
            image_assignment.completed = True
            image_assignment.completed_at = timezone.now()

        image_assignment.save()

        return Response({'success': True}, status=status.HTTP_200_OK)
