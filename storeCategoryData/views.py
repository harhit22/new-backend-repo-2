from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CategoryImage, ImageLabel
from .serializers import CategoryImageSerializer, ImageLabelSerializer


class CategoryImageViewSet(viewsets.ModelViewSet):
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer
    parser_classes = (MultiPartParser, FormParser)


class ImageLabelViewSet(viewsets.ModelViewSet):
    queryset = ImageLabel.objects.all()
    serializer_class = ImageLabelSerializer
