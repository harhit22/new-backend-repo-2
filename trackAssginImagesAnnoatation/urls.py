# trackAssginImagesAnnoatation/urls.py
from django.urls import path
from .views import NextImageView, UpdateImageStatusView

urlpatterns = [
    path('project/<int:project_id>/next-image/', NextImageView.as_view(), name='next-image'),
    path('project/assignment/<int:assignment_id>/<str:status>/', UpdateImageStatusView.as_view(), name='update-image-status'),
]
