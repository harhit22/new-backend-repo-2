# LabelCarftProjectSetup/tasks.py
from celery import shared_task
from django.core.files.storage import default_storage
from LabelCarftProjectSetup.models import Material, Toxicity, Condition, Grade, WasteType
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
from .helper_task.is_blur import blur
from .helper_task.is_rotate import rotate
from .helper_task.is_flipped_horizontally import flipped_horizontally
from .helper_task.is_bright import bright_image
from .helper_task.is_gray import grayscale
from .helper_task.is_crop import crop
from .helper_task.is_crop_hori import crop_hor
from .helper_task.is_crop_hor_30 import crop_hor_30

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def resize_with_padding(image, target_size=(640, 640), padding_color=(0, 0, 0)):
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
        total_images = train_images_num + val_images_num + test_images_num
        processed_images = 0
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
        for directory in [train_images_dir, val_images_dir, test_images_dir, train_labels_dir, val_labels_dir,
                          test_labels_dir]:
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
        test_images = category_images[
                      train_images_num + val_images_num:train_images_num + val_images_num + test_images_num]

        def clear_directory(self, directory):
            """Clear all files in a directory."""
            for file in directory.iterdir():
                if file.is_file():
                    file.unlink()

        def process_images(images, images_dir, labels_dir, is_rotated=True, is_flipped_horizontally=True,
                           is_scaled=True, is_bright=True, is_grayscale=True, is_crop=False, is_blur=True):
            nonlocal processed_images
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
                img = Image.fromarray(img)
                img.save(image_path)

                # Write labels for the image
                labels = ImageLabel.objects.filter(category_image=cat_image)
                label_path = os.path.join(labels_dir, f'{os.path.splitext(unique_image_name)[0]}.txt')

                with open(label_path, 'w') as f:
                    for label in labels:
                        class_id = classes.index(label.label)  # Get the class ID dynamically
                        x_min = min(label.x, label.x + label.width)
                        x_max = max(label.x, label.x + label.width)
                        y_min = min(label.y, label.y + label.height)
                        y_max = max(label.y, label.y + label.height)

                        label.x = x_min
                        label.y = y_min
                        label.width = x_max - x_min
                        label.height = y_max - y_min

                        # Calculate new bounding box coordinates
                        x_center = (label.x + label.width / 2) / cat_image.image_width
                        y_center = (label.y + label.height / 2) / cat_image.image_height
                        width = label.width / cat_image.image_width
                        height = label.height / cat_image.image_height

                        # Apply resizing adjustments to the bounding box
                        x_center = x_center * 640  # Resize the center to 640x640
                        y_center = y_center * 640  # Resize the center to 640x640
                        width = width * 640  # Resize the width to 640x640
                        height = height * 640  # Resize the height to 640x

                        # Normalize values for YOLO format
                        x_center /= 640
                        y_center /= 640
                        width /= 640
                        height /= 640

                        # Write the label in YOLO format
                        f.write(f'{class_id} {x_center} {y_center} {width} {height}\n')
                        logger.info(f'Label written: {class_id} {x_center} {y_center} {width} {height}')

                img_np = np.array(img)
                if is_rotated:
                    rotate(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image)
                if is_flipped_horizontally:
                    flipped_horizontally(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels,
                                         classes, cat_image)
                img = Image.open(image_path)
                img = resize_with_padding(img)
                img = Image.fromarray(cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB))
                img_np = np.array(img)
                if is_blur:
                    blur(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image)


                if is_bright:
                    bright_image(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes,
                                  cat_image)

                if is_grayscale:
                    grayscale(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes,
                                  cat_image)




                if is_scaled:
                    scale_factors = [1.5, 0.5]  # Example scaling factors

                    for scale_factor in scale_factors:
                        # Scale the image
                        scaled_width = int(cat_image.image_width * scale_factor)
                        scaled_height = int(cat_image.image_height * scale_factor)
                        img_scaled = cv2.resize(img_np, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)

                        # Create a blank canvas (black padding)
                        canvas = np.zeros((640, 640, 3), dtype=np.uint8)

                        if scale_factor < 1:  # Scale-Down: Add padding
                            # Center the smaller image on the canvas
                            x_offset = (640 - scaled_width) // 2
                            y_offset = (640 - scaled_height) // 2
                            canvas[y_offset:y_offset + scaled_height, x_offset:x_offset + scaled_width] = img_scaled

                            # Offset for bounding boxes (for smaller images)
                            x_box_offset = x_offset
                            y_box_offset = y_offset

                        else:  # Scale-Up: Crop the scaled image to fit 640x640
                            # Crop from the center
                            x_start = (scaled_width - 640) // 2 if scaled_width > 640 else 0
                            y_start = (scaled_height - 640) // 2 if scaled_height > 640 else 0
                            canvas = img_scaled[y_start:y_start + 640, x_start:x_start + 640]

                            # Offset for bounding boxes (for larger images)
                            x_box_offset = -x_start
                            y_box_offset = -y_start

                        # Save the final image
                        scaled_image_name = f"scaled_{scale_factor}_{image_counter}_{unique_image_name}"
                        scaled_image_path = os.path.join(images_dir, scaled_image_name)
                        cv2.imwrite(scaled_image_path, canvas)

                        # Save the adjusted labels
                        scaled_label_path = os.path.join(labels_dir, f'{os.path.splitext(scaled_image_name)[0]}.txt')
                        with open(scaled_label_path, 'w') as f:
                            for label in labels:
                                class_id = classes.index(label.label)  # Get the class ID dynamically

                                # Adjust bounding box coordinates for the scaled image
                                x_center = (label.x + label.width / 2) * scale_factor + x_box_offset
                                y_center = (label.y + label.height / 2) * scale_factor + y_box_offset
                                width = label.width * scale_factor
                                height = label.height * scale_factor

                                # Convert to absolute pixel values
                                x1 = (x_center - width / 2)
                                y1 = (y_center - height / 2)
                                x2 = (x_center + width / 2)
                                y2 = (y_center + height / 2)

                                # Ensure bounding box coordinates are within image bounds
                                x1 = max(0, x1)
                                y1 = max(0, y1)
                                x2 = min(640, x2)
                                y2 = min(640, y2)

                                # Convert back to YOLO format
                                x_center = (x1 + x2) / 2
                                y_center = (y1 + y2) / 2
                                width = x2 - x1
                                height = y2 - y1

                                # Normalize the bounding box for YOLO format (640x640)
                                x_center /= 640
                                y_center /= 640
                                width /= 640
                                height /= 640

                                # Write the label in YOLO format
                                f.write(f'{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n')
                                logger.info(
                                    f'Label written (scaled {scale_factor}): {class_id} {x_center} {y_center} {width} {height}')

                if is_crop:
                    crop(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes,
                                  cat_image)

                if is_crop:
                    crop_hor(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes,
                                  cat_image)
                    crop_hor_30(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes,
                                  cat_image)

                processed_images += 1
                progress = (processed_images / total_images) * 100
                self.update_state(state='PROGRESS',
                                  meta={'current': processed_images, 'total': total_images, 'percent': progress})


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
            for folder in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir, test_images_dir,
                           test_labels_dir]:
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, base_dir))
            zipf.write(yaml_file_path, os.path.relpath(yaml_file_path, base_dir))

        return {'success': f'YOLO dataset and zip file created at {zip_file_path}'}

    except Exception as e:
        return {'error': str(e)}
