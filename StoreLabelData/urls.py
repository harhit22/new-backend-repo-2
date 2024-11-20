from django.urls import path
from .views import ImageViewSet, LabelViewSet, list_dataset_files, get_image_id,\
    DeleteLabelsForImage
from django.views.decorators.csrf import csrf_exempt


# Map the actions to the appropriate viewset methods
image_create = csrf_exempt(ImageViewSet.as_view({'post': 'create'}))
label_create = LabelViewSet.as_view({'post': 'create'})

urlpatterns = [
    path('save_labeled_image/', image_create, name='save_labeled_image'),
    path('save_label_for_image/', label_create, name='save_label_for_image'),

    # getting already saved image
    path('api/<int:project_id>/labeledImage/', list_dataset_files, name='list_dataset_files'),

    # getting image id
    path('get_image_id/', get_image_id, name='get_image_id'),

    # updating labels
    path('delete_existing_labels/', DeleteLabelsForImage.as_view(), name='delete_existing_image')

]
