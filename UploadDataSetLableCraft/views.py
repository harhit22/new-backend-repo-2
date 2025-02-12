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
from .tasks import process_dataset_in_background, process_video_in_background
from firebase_admin import storage
import time
import uuid
import cv2
from django.db import transaction
from django.http import StreamingHttpResponse
import threading
import imghdr
from PIL import Image as IMG


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
            print('task started')
            process_dataset_in_background.delay(project_id, zip_path)
            print('task_ended')

            return JsonResponse({'success': True, 'message': 'Dataset is being processed in the background'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No file uploaded'})


def upload_image(request, project_id):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            project = get_object_or_404(Project, id=project_id)
            image = request.FILES['image']
            image_name = f"{uuid.uuid4()}_{int(time.time())}_{image.name}"
            temp_dir = 'temp_image_dir'
            os.makedirs(temp_dir, exist_ok=True)
            image_path = os.path.join(temp_dir, image_name)

            with open(image_path, 'wb+') as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)

            blob = storage.bucket().blob(f'projects/{project_id}/{image_name}')
            blob.upload_from_filename(image_path)
            blob.make_public()
            firebase_url = blob.public_url

            OriginalImage.objects.create(
                project=project,
                filename=image_name,
                firebase_url=firebase_url,
                assigned_to=None,
                status='unassigned'
            )

            if os.path.exists(image_path):
                os.remove(image_path)
                os.remove(temp_dir)

            return JsonResponse({'success': True, 'message': 'Image uploaded successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No image file uploaded'})


def upload_video(request, project_id):
    if request.method == 'POST' and request.FILES.get('video'):
        try:
            project = get_object_or_404(Project, id=project_id)
            video = request.FILES['video']
            video_name = video.name
            temp_dir = 'temp_video_dir'
            os.makedirs(temp_dir, exist_ok=True)
            video_path = os.path.join(temp_dir, video_name)

            # Save the uploaded video file temporarily
            with open(video_path, 'wb+') as temp_file:
                for chunk in video.chunks():
                    temp_file.write(chunk)

            # Start background task to process the video
            process_video_in_background.delay(project_id, video_path)
            os.remove(temp_dir)

            return JsonResponse({'success': True, 'message': 'Video is being processed in the background'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No video file uploaded'})


def upload_image_by_feed(request, project_id):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            project = get_object_or_404(Project, id=project_id)
            image = request.FILES['image']

            # Validate file type
            valid_formats = ['jpeg', 'png']
            file_type = imghdr.what(image)  # Check the image format

            temp_dir = 'temp_image_dir'
            os.makedirs(temp_dir, exist_ok=True)

            # Generate unique image name
            original_extension = image.name.split('.')[-1]
            image_name = f"{uuid.uuid4()}_{int(time.time())}.{original_extension}.jpg"
            temp_path = os.path.join(temp_dir, image_name)

            # Save the uploaded image temporarily
            with open(temp_path, 'wb+') as temp_file:
                for chunk in image.chunks():
                    temp_file.write(chunk)

            # Convert the image if the format is not valid
            if file_type not in valid_formats:
                converted_image_name = image_name.replace(original_extension, 'jpg')
                converted_image_path = os.path.join(temp_dir, converted_image_name)

                # Open and convert the image
                with IMG.open(temp_path) as img:  # Using IMG instead of Image
                    rgb_img = img.convert('RGB')  # Ensure the image is in RGB mode
                    rgb_img.save(converted_image_path, format='JPEG')

                os.remove(temp_path)  # Remove the original file
                image_path = converted_image_path  # Use the converted image
                image_name = converted_image_name  # Update the image name
            else:
                image_path = temp_path

            # Upload image to Firebase storage
            blob = storage.bucket().blob(f'projects/{project_id}/{image_name}')
            blob.upload_from_filename(image_path)
            blob.make_public()
            firebase_url = blob.public_url

            # Save image details in the database
            OriginalImage.objects.create(
                project=project,
                filename=image_name,
                firebase_url=firebase_url,
                assigned_to=None,
                status='unassigned'
            )

            # Clean up temporary files
            if os.path.exists(image_path):
                os.remove(image_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

            return JsonResponse({'success': True, 'message': 'Image uploaded successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'No image file uploaded'})


class NextImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        user = request.user

        # Ensure atomic transaction to prevent race conditions
        with transaction.atomic():
            # Lock any in-progress image for the user
            unassigned_image = OriginalImage.objects.select_for_update().filter(
                project=project,
                status='in_progress',
                assigned_to=user
            ).first()

            if unassigned_image is None:
                # Lock and get the next available unassigned image
                unassigned_image = OriginalImage.objects.select_for_update().filter(
                    project=project,
                    status='unassigned',
                    assigned_to__isnull=True
                ).first()

            if unassigned_image:
                # Update the OriginalImage status and assigned_to field within the locked transaction
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
                                status=status.HTTP_200_OK)


class CheckAlreadyLabelImage(APIView):

    def get(self, request, original_image_id):
        try:
            original_image_id = int(original_image_id)
            image = Image.objects.filter(original_image_id=original_image_id).first()
            if not image:
                try:
                    image = Image.objects.filter(id=original_image_id).first()
                except:
                    pass
            print(image)
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
        print(original_image, user, original_image.id)
        print(original_image.assigned_to)

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
            # print("i am making changes here")
            # original_image.status = 'unassigned'
            # original_image.save()
            # OriginalImage.objects.filter(id=original_image_id).update(assigned_to=None)
            return Response({"success": True, "message": "Status updated to unassigned."}, status=status.HTTP_200_OK)


class PreviousImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, current_image_id="undefined"):
        new_value = request.GET.get('new', 'false')
        user = get_object_or_404(User, id=user_id)
        project_id = request.GET.get('project_id', None)
        print(project_id)
        user_images = list(Image.objects.filter(uploaded_by=user, **({"project_id": project_id} if project_id else {})).order_by('-uploaded_at'))[1:]


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
                if new_value == 'true':
                    print(user_images)
                    print(current_index)
                    print('true is here')
                    if current_index < 1:
                        return Response({"error": "Current image not found in user's uploads"}, status=404)

                    previous_image = user_images[current_index -1]
                else:
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
