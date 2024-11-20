from rest_framework import generics
from StoreLabelData.serializers import ImageSerializer, CategoryImageStatusSerializer
from LabelCarftProjectSetup.models import ProjectCategory
from django.db.models import Subquery
from StoreLabelData.models import Label, CategoryImageStatus, Image
from storeCategoryData.models import ImageLabel, CategoryImage
from storeCategoryData.serializers import CategoryImageSerializer, ImageLabelSerializer
from StoreLabelData.views import LabelSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F


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


class AssignNextImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, category_id):
        user = request.user
        category = get_object_or_404(ProjectCategory, id=category_id)

        status_instance = CategoryImageStatus.objects.filter(
            category=category,
            status='in_progress',
            assigned_to=request.user,
        ).order_by('image__uploaded_at').first()
        print(status_instance)
        if status_instance is None:
            status_instance = CategoryImageStatus.objects.filter(
                category=category,
                status='unlabeled',
                assigned_to__isnull=True,
            ).order_by('image__uploaded_at').first()

        if status_instance is None:
            unassigned_image = Image.objects.filter(
                project_id=project_id
            ).exclude(
                category_statuses__category=category,
                category_statuses__assigned_to__isnull=False
            ).order_by('uploaded_at').first()
            if unassigned_image is None:
                return Response({"error": "No more images available"}, status=status.HTTP_403_FORBIDDEN)

            status_instance = CategoryImageStatus.objects.create(
                category=category,
                image=unassigned_image,
                assigned_to=user,
                status='in_progress'
            )
        else:
            status_instance.assigned_to = user
            status_instance.status = 'in_progress'
            status_instance.save()

        serializer = CategoryImageStatusSerializer(status_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateImageStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, image_id, cat_id):
        user = request.user
        cat_image_status = get_object_or_404(CategoryImageStatus, image__id=image_id, category__id=cat_id)

        if cat_image_status.assigned_to != user:
            return Response({"error": "You are not authorized to update this image"}, status=status.HTTP_403_FORBIDDEN)

        status_data = request.data.get('status', None)
        if status_data is None:
            return Response({"error": "Status data is missing from the request"}, status=status.HTTP_400_BAD_REQUEST)

        cat_image_status.status = status_data
        cat_image_status.save()

        return Response({"success": True, "status": cat_image_status.status}, status=status.HTTP_200_OK)


class CheckAndReassignCatImage(APIView):
    # permission_classes = [IsAuthenticated]

    def patch(self, request, image_id):
        user = request.user
        image = get_object_or_404(Image, id=image_id)

        try:
            print('hello')
            category_image = CategoryImage.objects.get(image=image)
            print(category_image)
            return Response({"success": False, "message": "Image already exists."}, status=status.HTTP_226_IM_USED)
        except CategoryImage.DoesNotExist:
            print('hello')
            category_image_status = get_object_or_404(CategoryImageStatus, image=image)
            category_image_status.status = 'unlabeled'
            category_image_status.assigned_to = None
            category_image_status.save()
            return Response({"success": True, "message": "Status updated to unassigned."}, status=status.HTTP_200_OK)


class ImageLabelDataView(generics.ListAPIView):
    serializer_class = LabelSerializer

    def get_queryset(self):
        image_id = self.kwargs['image_id']
        print(image_id, "i am image id")
        return Label.objects.filter(image_id=image_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GetAlreadyLabelCategoryImage(APIView):
    serializer_class = ImageSerializer

    def get(self, request, id, category):
        print({"id": id, "categ": category})
        try:
            # Try to get the object with image__id and category__id
            category_image = CategoryImage.objects.get(image__id=id, category__id=category)
            print({"cat": category_image})
            category_image_id = int(category_image.id)
            return Response(category_image_id, status=status.HTTP_200_OK)
        except CategoryImage.DoesNotExist:
            try:
                # If the first query fails, try getting with id and category__id
                category_image = CategoryImage.objects.get(id=id, category__id=category)
                print({"cat": category_image})
                category_image_id = int(category_image.id)
                return Response(category_image_id, status=status.HTTP_200_OK)
            except CategoryImage.DoesNotExist:
                # If both queries fail, return "none"
                print("I am here")
                return Response("none", status=status.HTTP_200_OK)



class DeleteAlreadyLabelCategoryImage(APIView):
    serializer_class = LabelSerializer

    def delete(self, request, category_id):
        labels_to_delete = ImageLabel.objects.filter(category_image_id=category_id)
        deleted_count, _ = labels_to_delete.delete()
        return JsonResponse({"success": True, "message": f"{deleted_count} labels deleted successfully"})


class PreviousImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, category, current_image_id="undefined"):
        # Get the user by ID
        user = get_object_or_404(User, id=user_id)

        # Filter CategoryImage based on the uploaded_by user and category, then order by updated_at
        user_images = list(CategoryImage.objects.filter(
            uploaded_by=user,
            category__category=category  # Filter by category name
        ).order_by('-updated_at'))  # Order by updated_at in descending order
        print(user_images)


        # Check if no images found for the user in the given category
        if not user_images:
            return Response({"error": "No images found for this category"}, status=404)

        # If current_image_id is undefined, return the first image (most recent one)
        if current_image_id == "undefined":
            previous_image = user_images[0]  # Get the first (most recent) image
            serializer = CategoryImageSerializer(previous_image)
            print(serializer)
            labels = ImageLabel.objects.filter(category_image=previous_image)
            label_serializer = ImageLabelSerializer(labels, many=True)
            print(label_serializer)
            response = {
                "image": serializer.data,
                "labels": label_serializer.data
            }
            return Response(response, status=200)
        else:
            # Find the current image's index in the filtered user_images list
            try:
                current_index = next(
                    idx for idx, img in enumerate(user_images) if img.id == current_image_id
                )
            except StopIteration:
                return Response({"error": "Current image not found in user's uploads"}, status=404)

            # Get the previous image if available
            if current_index + 1 < len(user_images):
                previous_image = user_images[current_index + 1]
                serializer = CategoryImageSerializer(previous_image)
                labels = ImageLabel.objects.filter(category_image=previous_image)
                label_serializer = ImageLabelSerializer(labels, many=True)
                response = {
                    "image": serializer.data,
                    "labels": label_serializer.data
                }
                return Response(response, status=200)
            else:
                return Response({"error": "No previous image available"}, status=404)

