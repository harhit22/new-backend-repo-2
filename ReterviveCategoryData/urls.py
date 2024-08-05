from django.urls import path
from .views import ImagesWithoutCategoryView, ImageLabelDataView, GetAlreadyLabelCategoryImage,\
    DeleteAlreadyLabelCategoryImage, AssignNextImageView, CheckAndReassignCatImage, UpdateImageStatusView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('images/without-category/<int:catId>/', ImagesWithoutCategoryView.as_view(), name='images_without_category'),
    path('Labels/labels/<int:image_id>/', ImageLabelDataView.as_view(), name='images_label_data'),
    path('get_label_image/<int:id>/<str:category>/', GetAlreadyLabelCategoryImage.as_view(), name='get_label_image'),
    path('delete_label_for_image_category/<str:category_id>/', DeleteAlreadyLabelCategoryImage.as_view(),
         name='delete_label_for_image_category'),

    path('next/<int:project_id>/<int:category_id>/', AssignNextImageView.as_view(),
         name='next-image-for-labling'),
    path('check_and_reassgin_cat_image/<int:image_id>/', CheckAndReassignCatImage.as_view(),
         name='reassign_image_for_category'),
    path('update_category_image_status/<int:image_id>/', UpdateImageStatusView.as_view(), name='update_image_status')
]
