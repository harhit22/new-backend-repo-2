from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CategoryImage, ImageLabel
from .serializers import CategoryImageSerializer, ImageLabelSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


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

    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)

        # Check if the 'labels' key exists in the request data
        if 'labels' in request.data:
            labels_data = request.data['labels']
            labels = []

            for label_data in labels_data:
                serializer = self.get_serializer(data=label_data)

                if serializer.is_valid():
                    serializer.save()  # Save the label data to the database
                    labels.append(serializer.data)
                else:
                    print("Validation failed for label:", label_data)
                    print(serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(labels, status=status.HTTP_201_CREATED)

        # If the 'labels' field is not present, handle it as a single label
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CategoryImageLabelDataView(APIView):
    def get(self, request, category_image_id):
        try:
            category_image = CategoryImage.objects.get(id=category_image_id)
            image_labels = ImageLabel.objects.filter(category_image=category_image)
            serializer = ImageLabelSerializer(image_labels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CategoryImage.DoesNotExist:
            return Response({"error": "CategoryImage not found"}, status=status.HTTP_404_NOT_FOUND)
