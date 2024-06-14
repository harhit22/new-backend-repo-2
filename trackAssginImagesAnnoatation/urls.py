from django.urls import path
from . import views

urlpatterns = [
    path('assign-image/<int:project_id>/', views.assign_image, name='assign_image'),
    path('complete-image-labeling/<int:project_id>/<int:image_id>/', views.complete_image_labeling, name='complete_image_labeling'),
]
