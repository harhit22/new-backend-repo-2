from django.urls import path
from . import user_view, views


urlpatterns = [
    path("get-all-user/", user_view.GetAllUserAdmin.as_view(), name="get-all-user"),
    path("all-images/<int:project_id>/", views.OriginalImageListView.as_view(), name="get-all-images"),
    path("annotated-images/<int:project_id>/", views.AnnotatedImageListView.as_view(), name="annotated-images"),
    path("labeled-images/<int:project_id>/", views.LabeledImageListView.as_view(), name="labeled-images")
]



