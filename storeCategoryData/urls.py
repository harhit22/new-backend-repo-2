from django.urls import path
from .views import CategoryImageViewSet, ImageLabelViewSet
from django.views.decorators.csrf import csrf_exempt


# Map the actions to the appropriate viewset methods
image_create = csrf_exempt(CategoryImageViewSet.as_view({'post': 'create'}))
label_create = ImageLabelViewSet.as_view({'post': 'create'})

urlpatterns = [
    path('save_category_labeled_image/', image_create, name='save_labeled_image'),
    path('save_category_label_for_image/', label_create, name='save_label_for_image'),

]
