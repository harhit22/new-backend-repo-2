from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import Project, ProjectInvitation
from LabelCarftProjectSetup.serializers import ProjectSerializer, ProjectInvitationSerializer
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from django.shortcuts import redirect
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q



class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project_name = self.request.data.get('name')
        if Project.objects.filter(name=project_name).exists():
            raise ValidationError('A project with this name already exists.')
        serializer.save(created_by=self.request.user)


class SendInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if project.created_by != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)


        email = request.data.get('emails')
        print(email)
        if not email:
            return Response({'email': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        invitation = ProjectInvitation.objects.create(project=project, email=email[0])
        send_mail(
            'Project Invitation',
            f'You have been invited to join the project "{project.name}". Use this link to accept: http://127.0.0.1:8000/project/invitations/{invitation.token}/accept/',
            'from@example.com',
            [email[0]],
            fail_silently=False,
        )

        return Response(ProjectInvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class AcceptInvitationView(APIView):
    queryset = ProjectInvitation.objects.all()
    serializer_class = ProjectInvitationSerializer
    permission_classes = [permissions.AllowAny, DjangoModelPermissionsOrAnonReadOnly]

    def get(self, request, *args, **kwargs):
        token = self.kwargs['token']
        invitation = get_object_or_404(ProjectInvitation, token=token)

        if invitation.accepted:
            return Response({'detail': 'Invitation already accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        email = invitation.email
        try:
            user = User.objects.get(email=email)
            invitation.project.members.add(user)
            invitation.accepted = True
            invitation.registered_user = user
            invitation.save()
            return Response({'detail': 'Invitation accepted.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # User not found, redirect to registration page
            pass

        return Response({'detail': 'Authentication required. Please register to accept the invitation.'}, status=status.HTTP_401_UNAUTHORIZED)


class ProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

        projects = Project.objects.filter(
            Q(created_by=user) |
            Q(members=user)
        ).distinct()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



