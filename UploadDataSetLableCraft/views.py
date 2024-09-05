from django.http import JsonResponse
import os
import shutil
import zipfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from LabelCarftProjectSetup.models import Project
from .models import OriginalImage
from StoreLabelData.models import Image, Label
from django.core.exceptions import ObjectDoesNotExist
from StoreLabelData.serializers import ImageSerializer, LabelSerializer
from django.contrib.auth.models import User
from cinx_backend.firebase import bucket



def upload_dataset(request, project_id):
    if request.method == 'POST' and request.FILES.get('dataset'):
        project = get_object_or_404(Project, id=project_id)
        dataset = request.FILES['dataset']

        temp_dir = 'temp_extract_dir'
        os.makedirs(temp_dir, exist_ok=True)

        try:
            zip_path = os.path.join(temp_dir, 'uploaded_dataset.zip')
            with open(zip_path, 'wb+') as destination:
                for chunk in dataset.chunks():
                    destination.write(chunk)

            extract_path = f'{temp_dir}/extracted/'
            os.makedirs(extract_path, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            os.remove(zip_path)

            # Create OriginalImage entries and upload to Firebase
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, extract_path)

                    # Upload file to Firebase Storage
                    blob = bucket.blob(f'projects/{project_id}/{file}')
                    blob.upload_from_filename(file_path)
                    blob.make_public()
                    firebase_url = blob.public_url

                    # Save the OriginalImage record with Firebase URL
                    OriginalImage.objects.create(
                        project=project,
                        filename=file,
                        firebase_url=firebase_url,
                        assigned_to=None,
                        status='unassigned'
                    )

            # Clean up temporary files
            shutil.rmtree(temp_dir)

            return JsonResponse({'success': True})
        except zipfile.BadZipFile:
            os.remove(zip_path)
            shutil.rmtree(temp_dir)
            return JsonResponse({'success': False, 'error': 'Invalid zip file'})
        except Exception as e:
            shutil.rmtree(temp_dir)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No file uploaded'})


class NextImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        user = request.user
        unassigned_image = OriginalImage.objects.filter(
            project=project,
            status='in_progress',
            assigned_to=user
        ).first()
        if unassigned_image == None:
            unassigned_image = OriginalImage.objects.filter(
                project=project,
                status='unassigned',
            ).first()

        if unassigned_image:
            # Update the OriginalImage status and assigned_to field
            unassigned_image.status = 'in_progress'
            unassigned_image.assigned_to = user
            unassigned_image.save()

            # Prepare the response data with the image path
            response_data = {
                'image_id': unassigned_image.id,
                'project_id': unassigned_image.project.id,
                'filename': unassigned_image.filename,
                'image_path': unassigned_image.firebase_url,
                'user': unassigned_image.assigned_to.id,
                'complete': unassigned_image.completed,
                'status': unassigned_image.status
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'error': 'No unassigned images available'},
                            status=status.HTTP_404_NOT_FOUND)


class CheckAlreadyLabelImage(APIView):

    def get(self, request, original_image_id):
        try:
            original_image_id = int(original_image_id)
            image = Image.objects.filter(original_image_id=original_image_id).first()
            if image:
                return Response(image.id, status=status.HTTP_200_OK)
            else:
                return Response(False, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Invalid original_image_id provided."}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(False, status=status.HTTP_200_OK)


class UpdateImageStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, original_image_id):
        user = request.user
        original_image = get_object_or_404(OriginalImage, id=original_image_id)
        print(original_image, user)

        if original_image.assigned_to != user:
            return Response({"error": "You are not authorized to update this image"}, status=status.HTTP_403_FORBIDDEN)

        status_data = request.data.get('status', None)
        print(status_data)
        if status_data is None:
            return Response({"error": "Status data is missing from the request"}, status=status.HTTP_400_BAD_REQUEST)

        original_image.status = status_data
        original_image.save()

        return Response({"success": True, "status": original_image.status}, status=status.HTTP_200_OK)


class CheckAndReassignStatus(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, original_image_id):
        user = request.user
        original_image = get_object_or_404(OriginalImage, id=original_image_id)

        try:
            image = Image.objects.get(original_image=original_image)
            print(image, 'imageeeeee')
            return Response({"success": False, "message": "Image already exists."}, status=status.HTTP_226_IM_USED)
        except Image.DoesNotExist:
            original_image.status = 'unassigned'
            original_image.save()
            OriginalImage.objects.filter(id=original_image_id).update(assigned_to=None)
            return Response({"success": True, "message": "Status updated to unassigned."}, status=status.HTTP_200_OK)


class PreviousImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, current_image_id="undefined"):
        user = get_object_or_404(User, id=user_id)
        user_images = list(Image.objects.filter(uploaded_by=user).order_by('-uploaded_at'))
        print(user_images)

        if current_image_id == "undefined":
            previous_image = user_images[0]
            serializer = ImageSerializer(previous_image)
            print(serializer.data)
            labels = Label.objects.filter(image=previous_image)
            label_serializer = LabelSerializer(labels, many=True)
            label_data = label_serializer.data
            response = {
                "image": serializer.data,
                'labels': label_data
            }
            return Response(response, status=200)
        else:
            try:
                current_index = next(
                    idx for idx, img in enumerate(user_images) if img.id == current_image_id
                )
                print(current_index)
            except StopIteration:
                return Response({"error": "Current image not found in user's uploads"}, status=404)

            try:
                previous_image = user_images[current_index + 1]
                serializer = ImageSerializer(previous_image)
                labels = Label.objects.filter(image=previous_image)
                label_serializer = LabelSerializer(labels, many=True)
                label_data = label_serializer.data
                response = {
                    "image": serializer.data,
                    'labels': label_data
                }
                return Response(response, status=200)
            except:
                return Response({"error": "Current image not found in user's uploads"}, status=404)
