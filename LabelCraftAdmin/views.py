from rest_framework import generics
from UploadDataSetLableCraft.models import OriginalImage
from .serializers import OriginalImageSerializer, AnnotatedImageSerializer, LabeledImageSerializer
from storeCategoryData.models import CategoryImage
from StoreLabelData.models import Image
from rest_framework import generics
from rest_framework.response import Response
from UploadDataSetLableCraft.models import OriginalImage
from .serializers import OriginalImageSerializer
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 16  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size a user can request


class OriginalImageListView(generics.ListAPIView):
    queryset = OriginalImage.objects.all()
    serializer_class = OriginalImageSerializer
    pagination_class = StandardResultsSetPagination



    def get_paginated_response(self, data):
        paginator = self.paginator
        request = self.request
        page = paginator.page
        return Response({
            'count': paginator.page.paginator.count,
            'next': self.get_next_page_link(request, page),
            'previous': self.get_previous_page_link(request, page),
            'results': data,
            'page_size': self.paginator.page_size
        })

    def get_next_page_link(self, request, page):
        if page.has_next():
            next_page_number = page.next_page_number()
            return request.build_absolute_uri(f'?page={next_page_number}')
        return None

    def get_previous_page_link(self, request, page):
        if page.has_previous():
            previous_page_number = page.previous_page_number()
            return request.build_absolute_uri(f'?page={previous_page_number}')
        return None


class AnnotatedImageListView(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = AnnotatedImageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        uploaded_by = self.request.query_params.get('uploaded_by', None)
        if uploaded_by:
            queryset = queryset.filter(uploaded_by__username=uploaded_by)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_paginated_response(self, data):
        paginator = self.paginator
        request = self.request
        page = paginator.page

        return Response({
            'count': paginator.page.paginator.count,
            'next': self.get_next_page_link(request, page),
            'previous': self.get_previous_page_link(request, page),
            'results': data,
            'page_size': paginator.page_size,
        })

    def get_next_page_link(self, request, page):
        if page.has_next():
            next_page_number = page.next_page_number()
            return request.build_absolute_uri(f'?page={next_page_number}')
        return None

    def get_previous_page_link(self, request, page):
        if page.has_previous():
            previous_page_number = page.previous_page_number()
            return request.build_absolute_uri(f'?page={previous_page_number}')
        return None


class LabeledImageListView(generics.ListAPIView):
    queryset = CategoryImage.objects.all()
    serializer_class = LabeledImageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Override get_queryset to filter by uploaded_by and category_name if provided in query params.
        """
        queryset = super().get_queryset()

        uploaded_by = self.request.query_params.get('uploaded_by', None)
        category_name = self.request.query_params.get('category_name', None)

        if uploaded_by:
            queryset = queryset.filter(uploaded_by__username=uploaded_by)

        if category_name:
            queryset = queryset.filter(category__category=category_name)

        return queryset

    def get_paginated_response(self, data):
        paginator = self.paginator
        request = self.request
        page = paginator.page
        return Response({
            'count': paginator.page.paginator.count,
            'next': self.get_next_page_link(request, page),
            'previous': self.get_previous_page_link(request, page),
            'results': data,
            'page_size': self.paginator.page_size
        })

    def get_next_page_link(self, request, page):
        if page.has_next():
            next_page_number = page.next_page_number()
            return request.build_absolute_uri(f'?page={next_page_number}')
        return None

    def get_previous_page_link(self, request, page):
        if page.has_previous():
            previous_page_number = page.previous_page_number()
            return request.build_absolute_uri(f'?page={previous_page_number}')
        return None
