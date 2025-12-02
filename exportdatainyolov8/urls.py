from django.urls import path
from .views import DatasetDownloadView, TotalImagesByCategoryView, TaskStatusView,  ProcessImageTask, GetDataForMonitoringTeamWasteCollectionAllCityApi, GetDataForMonitoringTeamWasteCollectionApi

urlpatterns = [
    path('download-dataset/', DatasetDownloadView.as_view(), name='download_dataset'),
    path('category-image-count/', TotalImagesByCategoryView.as_view(), name='download_dataset'),
    path('task-status/', TaskStatusView.as_view(), name='task_status'),
    path('process-images-extra', ProcessImageTask.as_view(), name='process-task-extra'),
    path('get-waste-data/', GetDataForMonitoringTeamWasteCollectionApi.as_view(), name='get-waste-data'),
    path('get-waste-data-all-city/', GetDataForMonitoringTeamWasteCollectionAllCityApi.as_view(), name='get-waste-data'),
]
