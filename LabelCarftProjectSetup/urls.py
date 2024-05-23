from django.urls import path
from .views import ProjectCreateView, SendInvitationView, AcceptInvitationView, ProjectListView

urlpatterns = [
    path('api/create/', ProjectCreateView.as_view(), name='project-create'),
    path('api/<int:project_id>/invite/', SendInvitationView.as_view(), name='send-invitation'),
    path('invitations/<str:token>/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
]

