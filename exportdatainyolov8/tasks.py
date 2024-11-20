# LabelCarftProjectSetup/tasks.py

from celery import shared_task
from django.core.files.storage import default_storage
from LabelCarftProjectSetup.models import  Material, Toxicity, Condition, Grade, WasteType
from storeCategoryData.models import CategoryImage, ImageLabel
from pathlib import Path
import requests
import os
from PIL import Image
import random
import yaml
import zipfile
import cv2
import numpy as np
import logging

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def resize_with_padding(image, target_size=(640, 640), padding_color=(0, 0, 0)):
    """
    Resize an image to a target size while preserving the aspect ratio.
    Adds padding to reach the exact dimensions if necessary.

    Parameters:
    - image: Input image (numpy array).
    - target_size: Tuple of desired (width, height) size.
    - padding_color: Tuple for padding color (B, G, R).

    Returns:
    - Padded and resized image as a numpy array.
    """

    if not isinstance(image, np.ndarray):
        image = np.array(image)

    # Original dimensions
    h, w = image.shape[:2]
    target_w, target_h = target_size

    # Calculate the scaling factor and new dimensions
    scale = min(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Resize the image with the calculated new dimensions
    resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Calculate padding to reach the target dimensions
    delta_w = target_w - new_w
    delta_h = target_h - new_h
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    # Add padding
    padded_image = cv2.copyMakeBorder(resized_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)

    return padded_image


@shared_task(bind=True)
def generate_yolo_dataset(self, category_id, category_name, train_images_num, val_images_num, test_images_num, is_blur):
    try:
        # Map category names to their corresponding models
        model_mapping = {
            'Material': Material,
            'Toxicity': Toxicity,
            'Condition': Condition,
            'Grade': Grade,
            'WasteType': WasteType,
        }

        model_class = model_mapping.get(category_name)

        if not model_class:
            return {'error': 'Invalid category name'}

        # Fetch data from the database
        data = list(model_class.objects.filter(category_id=category_id).values('id', 'name'))

        # Create YOLO dataset directories
        base_dir = Path('dataset')
        images_dir = base_dir / 'images'
        labels_dir = base_dir / 'labels'
        train_images_dir = images_dir / 'train'
        val_images_dir = images_dir / 'val'
        test_images_dir = images_dir / 'test'
        train_labels_dir = labels_dir / 'train'
        val_labels_dir = labels_dir / 'val'
        test_labels_dir = labels_dir / 'test'

        for directory in [base_dir, images_dir, labels_dir, train_images_dir, val_images_dir, test_images_dir,
                          train_labels_dir, val_labels_dir, test_labels_dir]:
            os.makedirs(directory, exist_ok=True)

        # Clear directories before creating new dataset
        for directory in [train_images_dir, val_images_dir, test_images_dir, train_labels_dir, val_labels_dir, test_labels_dir]:
            for file in directory.iterdir():
                if file.is_file():
                    file.unlink()

        # Fetch class names and images for the dataset
        classes = list(model_class.objects.filter(category_id=category_id).values_list('name', flat=True))
        category_images = list(CategoryImage.objects.filter(category_id=category_id))
        random.shuffle(category_images)

        # Split the data
        train_images = category_images[:train_images_num]
        val_images = category_images[train_images_num:train_images_num + val_images_num]
        test_images = category_images[train_images_num + val_images_num:train_images_num + val_images_num + test_images_num]

        def clear_directory(self, directory):
            """Clear all files in a directory."""
            for file in directory.iterdir():
                if file.is_file():
                    file.unlink()

        def process_images(images, images_dir, labels_dir):
            image_counter = 0
            for cat_image in images:
                # Fetch and save image
                original_image_name = os.path.basename(cat_image.firebase_url.split()[-1])
                unique_image_name = f"{image_counter}_{original_image_name}"
                image_path = os.path.join(images_dir, unique_image_name)
                response = requests.get(cat_image.firebase_url)

                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)

                # Resize and save image
                img = Image.open(image_path)
                img = resize_with_padding(img)
                img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                img.save(image_path)

                # Write labels for the image
                labels = ImageLabel.objects.filter(category_image=cat_image)
                label_path = os.path.join(labels_dir, f'{os.path.splitext(unique_image_name)[0]}.txt')

                with open(label_path, 'w') as f:
                    for label in labels:
                        class_id = classes.index(label.label)  # Get the class ID dynamically
                        if label.width < 0 and label.height < 0:
                            label.x = abs(label.x - label.width)
                            label.y = abs(label.y - label.height)
                            label.width = label.x
                            label.height = label.y

                        # Calculate new bounding box coordinates
                        x_center = (label.x + label.width / 2) / cat_image.image_width
                        y_center = (label.y + label.height / 2) / cat_image.image_height
                        width = label.width / cat_image.image_width
                        height = label.height / cat_image.image_height

                        # Apply resizing adjustments to the bounding box
                        x_center = x_center * 640  # Resize the center to 640x640
                        y_center = y_center * 640  # Resize the center to 640x640
                        width = width * 640  # Resize the width to 640x640
                        height = height * 640  # Resize the height to 640x640

                        # Normalize values for YOLO format
                        x_center /= 640
                        y_center /= 640
                        width /= 640
                        height /= 640

                        # Write the label in YOLO format
                        f.write(f'{class_id} {x_center} {y_center} {width} {height}\n')
                        logger.info(f'Label written: {class_id} {x_center} {y_center} {width} {height}')

                img_np = np.array(img)
                if is_blur:
                    blurred_image_name = f"blurred_{image_counter}_{unique_image_name}"
                    blurred_image_path = os.path.join(images_dir, blurred_image_name)
                    img_blurred = cv2.GaussianBlur(img_np, (5, 5), 0)
                    cv2.imwrite(blurred_image_path, img_blurred)

                    # Save the same labels for the blurred image, adjusting the bounding boxes
                    blurred_label_path = os.path.join(labels_dir, f'{os.path.splitext(blurred_image_name)[0]}.txt')
                    with open(blurred_label_path, 'w') as f:
                        for label in labels:
                            class_id = classes.index(label.label)  # Get the class ID dynamically
                            if label.width < 0 and label.height < 0:
                                label.x = abs(label.x - label.width)
                                label.y = abs(label.y - label.height)
                                label.width = label.x
                                label.height = label.y

                            # Calculate new bounding box coordinates
                            x_center = (label.x + label.width / 2) / cat_image.image_width
                            y_center = (label.y + label.height / 2) / cat_image.image_height
                            width = label.width / cat_image.image_width
                            height = label.height / cat_image.image_height

                            # Apply resizing adjustments to the bounding box
                            x_center = x_center * 640  # Resize the center to 640x640
                            y_center = y_center * 640  # Resize the center to 640x640
                            width = width * 640  # Resize the width to 640x640
                            height = height * 640  # Resize the height to 640x640

                            # Normalize values for YOLO format
                            x_center /= 640
                            y_center /= 640
                            width /= 640
                            height /= 640

                            # Write the label in YOLO format
                            f.write(f'{class_id} {x_center} {y_center} {width} {height}\n')
                            logger.info(f'Label written: {class_id} {x_center} {y_center} {width} {height}')

                image_counter += 1

        # Process images for train, val, and test datasets
        process_images(train_images, train_images_dir, train_labels_dir)
        process_images(val_images, val_images_dir, val_labels_dir)
        process_images(test_images, test_images_dir, test_labels_dir)

        # Create YAML file for the dataset
        yaml_content = {
            'train': str(train_images_dir),
            'val': str(val_images_dir),
            'test': str(test_images_dir),
            'nc': len(classes),
            'names': classes,
        }
        yaml_file_path = os.path.join(base_dir, 'dataset_config.yaml')
        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump(yaml_content, yaml_file)

        # Create ZIP file containing the dataset
        zip_file_path = os.path.join(base_dir, 'yolo_dataset.zip')
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir, test_images_dir, test_labels_dir]:
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, base_dir))
            zipf.write(yaml_file_path, os.path.relpath(yaml_file_path, base_dir))

        return {'success': f'YOLO dataset and zip file created at {zip_file_path}'}

    except Exception as e:
        return {'error': str(e)}


