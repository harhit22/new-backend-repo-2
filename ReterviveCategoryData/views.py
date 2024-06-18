from rest_framework import generics
from StoreLabelData.models import Image
from storeCategoryData.models import CategoryImage
from StoreLabelData.serializers import ImageSerializer
from django.db.models import Subquery
from StoreLabelData.models import Label
from storeCategoryData.models import ImageLabel
from StoreLabelData.views import LabelSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView


class ImagesWithoutCategoryView(generics.ListAPIView):
    serializer_class = ImageSerializer

    def get_queryset(self):
        category_id = self.kwargs['catId']
        if not CategoryImage.objects.exists():
            queryset = Image.objects.all()
        else:
            category_image_subquery = CategoryImage.objects.filter(category_id=category_id).values('image_id')
            queryset = Image.objects.exclude(id__in=Subquery(category_image_subquery))

        return queryset


class ImageLabelDataView(generics.ListAPIView):
    serializer_class = LabelSerializer

    def get_queryset(self):
        image_id = self.kwargs['image_id']
        return Label.objects.filter(image_id=image_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GetAlreadyLabelCategoryImage(APIView):
    serializer_class = ImageSerializer

    def get(self, request, id, category):
        try:

            category_image = CategoryImage.objects.get(image__id=id, category__id=category)
            print(category_image)
            category_image = int(category_image.id)
            return Response(category_image, status=status.HTTP_200_OK)
        except CategoryImage.DoesNotExist:
            return Response("none", status=status.HTTP_200_OK)


class DeleteAlreadyLabelCategoryImage(APIView):
    serializer_class = LabelSerializer

    def delete(self, request, category_id):
        labels_to_delete = ImageLabel.objects.filter(category_image_id=category_id)
        deleted_count, _ = labels_to_delete.delete()
        return JsonResponse({"success": True, "message": f"{deleted_count} labels deleted successfully"})
