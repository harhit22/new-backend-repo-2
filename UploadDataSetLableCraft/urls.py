from django.urls import path
from . import views
from .views import NextImageView, CheckAlreadyLabelImage, UpdateImageStatusView, CheckAndReassignStatus
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/<int:project_id>/upload_dataset/',  csrf_exempt(views.upload_dataset), name='upload_dataset'),
    path('api/<int:project_id>/next-image/',  NextImageView.as_view(), name='upload_dataset'),
    path('api/check_already_annotated_image/<int:original_image_id>/', CheckAlreadyLabelImage.as_view(),
         name='check_already_annotated_image'),
    path('update_image_status/<int:original_image_id>/', UpdateImageStatusView.as_view(), name='update_image_status'),
    path('check_and_reassign_status/<int:original_image_id>/', CheckAndReassignStatus.as_view(), name='update_image_status'),

]