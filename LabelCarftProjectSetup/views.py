from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import Project, ProjectInvitation
from LabelCarftProjectSetup.serializers import ProjectSerializer, ProjectInvitationSerializer


class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SendInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if project.created_by != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        if not email:
            return Response({'email': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        invitation = ProjectInvitation.objects.create(project=project, email=email)
        send_mail(
            'Project Invitation',
            f'You have been invited to join the project "{project.name}". Use this link to accept: http://example.com/invitations/{invitation.token}/accept/',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        return Response(ProjectInvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class AcceptInvitationView(APIView):
    def post(self, request, token):
        invitation = get_object_or_404(ProjectInvitation, token=token)
        if invitation.accepted:
            return Response({'detail': 'Invitation already accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        invitation.project.members.add(user)
        invitation.accepted = True
        invitation.registered_user = user
        invitation.save()

        return Response({'detail': 'Invitation accepted.'}, status=status.HTTP_200_OK)

class RegisterViaInvitationView(APIView):
    def post(self, request, token):
        invitation = get_object_or_404(ProjectInvitation, token=token)
        if invitation.accepted:
            return Response({'detail': 'Invitation already accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        email = invitation.email
        password = request.data.get('password')

        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        invitation.project.members.add(user)
        invitation.accepted = True
        invitation.registered_user = user
        invitation.save()

        return Response({'detail': 'Registration and invitation acceptance successful.'}, status=status.HTTP_201_CREATED)
