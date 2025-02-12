# app_name/tasks.py
import os
import zipfile
import shutil
from celery import shared_task
from django.shortcuts import get_object_or_404
from UploadDataSetLableCraft.models import OriginalImage, Project
from firebase_admin import storage
import logging
import cv2
import time
import uuid

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_dataset_in_background(self, project_id, dataset_path):
    logger.info('Task started: Processing dataset in the background')

    project = get_object_or_404(Project, id=project_id)
    temp_dir = 'temp_extract_dir'
    extract_path = f'{temp_dir}/extracted/'

    try:
        # Extract the ZIP file
        with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        logger.info('Zip file extracted successfully')

        # Upload images to Firebase and save in the database
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                file_path = os.path.join(root, file)
                file = f"{uuid.uuid4()}_{int(time.time())}_{file}"
                # Upload file to Firebase Storage
                blob = storage.bucket().blob(f'projects/{project_id}/{file}')
                blob.upload_from_filename(file_path)
                blob.make_public()
                firebase_url = blob.public_url

                # Save the OriginalImage record with Firebase URL
                try:
                    OriginalImage.objects.create(
                        project=project,
                        filename=file,
                        firebase_url=firebase_url,
                        assigned_to=None,
                        status='unassigned'
                    )
                except Exception as e:
                    raise Exception(f"Failed to create OriginalImage: {str(e)}")

                logger.info(f'Uploaded file {file} to Firebase and saved in database')

        # Clean up temporary files
        shutil.rmtree(temp_dir)
        logger.info('Temporary directory cleaned up')

    except zipfile.BadZipFile:
        shutil.rmtree(temp_dir)
        logger.error('Invalid zip file encountered', exc_info=True)
        raise Exception('Invalid zip file')
    except Exception as e:
        shutil.rmtree(temp_dir)
        logger.error(f'Error processing dataset: {e}', exc_info=True)
        raise Exception(str(e))

@shared_task
def process_video_in_background(project_id, video_path):
    try:
        project = get_object_or_404(Project, id=project_id)
        video_capture = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            # Only save every 30th frame
            if frame_count % 30 == 0:
                # Resize the frame to 640x640
                resized_frame = cv2.resize(frame, (640, 640))
                frame_name = f'frame_{frame_count}.jpg'  # Frame naming
                frame_name = f"{uuid.uuid4()}_{int(time.time())}_{frame_name}"

                # Save the frame as an image temporarily
                temp_frame_path = f'temp_frame_{frame_count}.jpg'
                cv2.imwrite(temp_frame_path, resized_frame)

                # Upload the frame to storage
                blob = storage.bucket().blob(f'projects/{project_id}/{frame_name}')
                blob.upload_from_filename(temp_frame_path)
                blob.make_public()  # Make the uploaded frame public

                # Create a record for the uploaded image
                OriginalImage.objects.create(
                    project=project,
                    filename=frame_name,
                    firebase_url=blob.public_url,
                    assigned_to=None,
                    status='unassigned'
                )

                # Clean up temporary frame file
                os.remove(temp_frame_path)

            frame_count += 1

        video_capture.release()
        if os.path.exists(video_path):
            os.remove(video_path)

        return {'success': True, 'message': f'{frame_count // 30} frames uploaded successfully!'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

