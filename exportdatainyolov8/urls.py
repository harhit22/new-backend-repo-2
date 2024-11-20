from django.urls import path
from .views import DatasetDownloadView, TotalImagesByCategoryView, TaskStatusView

urlpatterns = [
    path('download-dataset/', DatasetDownloadView.as_view(), name='download_dataset'),
    path('category-image-count/', TotalImagesByCategoryView.as_view(), name='download_dataset'),
    path('task-status/', TaskStatusView.as_view(), name='task_status'),
]
