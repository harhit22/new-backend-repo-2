from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CategoryImage, ImageLabel
from .serializers import CategoryImageSerializer, ImageLabelSerializer
from rest_framework.response import Response


class CategoryImageViewSet(viewsets.ModelViewSet):
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ImageLabelViewSet(viewsets.ModelViewSet):
    queryset = ImageLabel.objects.all()
    serializer_class = ImageLabelSerializer
