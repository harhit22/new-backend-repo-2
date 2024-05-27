from django.urls import path
from . import views

urlpatterns = [
    # ... other paths ...
    path('api/<int:project_id>/dataset/', views.list_dataset_files, name='list_dataset_files'),
]
