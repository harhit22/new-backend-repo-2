from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/<int:project_id>/upload_dataset/',  csrf_exempt(views.upload_dataset), name='upload_dataset'),
    path('api/<int:project_id>/upload_dataset_extend/',  csrf_exempt(views.upload_dataset_extend), name='upload_dataset_extend'),
]