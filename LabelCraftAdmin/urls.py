from django.urls import path
from . import user_view, views


urlpatterns = [
    path("get-all-user/", user_view.GetAllUserAdmin.as_view(), name="get-all-user"),
    path("all-images/", views.OriginalImageListView.as_view(), name="get-all-images"),
    path("annotated-images/", views.AnnotatedImageListView.as_view(), name="get-all-images"),
    path("labeled-images/", views.LabeledImageListView.as_view(), name="get-all-images")
]



