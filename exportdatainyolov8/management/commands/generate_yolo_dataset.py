import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from storeCategoryData.models import CategoryImage, ImageLabel
import random
import yaml


class Command(BaseCommand):
    help = 'Generate YOLOv8 dataset'

    def handle(self, *args, **options):
        # Define your paths
        base_dir = Path('dataset')
        images_dir = base_dir / 'images'
        labels_dir = base_dir / 'labels'
        train_images_dir = images_dir / 'train'
        val_images_dir = images_dir / 'val'
        test_images_dir = images_dir / 'test'
        train_labels_dir = labels_dir / 'train'
        val_labels_dir = labels_dir / 'val'
        test_labels_dir = labels_dir / 'test'

        # Create directories if they don't exist
        train_images_dir.mkdir(parents=True, exist_ok=True)
        val_images_dir.mkdir(parents=True, exist_ok=True)
        test_images_dir.mkdir(parents=True, exist_ok=True)
        train_labels_dir.mkdir(parents=True, exist_ok=True)
        val_labels_dir.mkdir(parents=True, exist_ok=True)
        test_labels_dir.mkdir(parents=True, exist_ok=True)

        # Function to copy images and create label files
        self.create_yolo_dataset(base_dir, train_images_dir, train_labels_dir, val_images_dir, val_labels_dir,
                                 test_images_dir, test_labels_dir)

    def create_yolo_dataset(self, base_dir, train_images_dir, train_labels_dir, val_images_dir, val_labels_dir,
                            test_images_dir, test_labels_dir):
        # Get data from the database
        category_images = list(CategoryImage.objects.all())

        # Shuffle and split the data
        random.shuffle(category_images)
        total_images = len(category_images)
        train_split = int(0.7 * total_images)
        val_split = int(0.2 * total_images)

        train_images = category_images[:train_split]
        val_images = category_images[train_split:train_split + val_split]
        test_images = category_images[train_split + val_split:]

        # Function to process and save images and labels
        def process_images(images, images_dir, labels_dir):
            for cat_image in images:
                image_name = os.path.basename(cat_image.image_file.name)
                image_path = images_dir / image_name

                # Copy image file to the dataset directory
                with cat_image.image_file.open() as img:
                    with open(image_path, 'wb') as f:
                        shutil.copyfileobj(img, f)

                # Create corresponding label file
                labels = ImageLabel.objects.filter(category_image=cat_image)
                label_path = labels_dir / f'{image_path.stem}.txt'

                with open(label_path, 'w') as f:
                    for label in labels:
                        class_id = 0 if label.label == 'Tyre' else 1  # Assuming Dirty=0 and Fair=1
                        x_center = (label.x + label.width / 2) / cat_image.image_width
                        y_center = (label.y + label.height / 2) / cat_image.image_height
                        width = label.width / cat_image.image_width
                        height = label.height / cat_image.image_height

                        f.write(f'{class_id} {x_center} {y_center} {width} {height}\n')

        # Process each split
        process_images(train_images, train_images_dir, train_labels_dir)
        process_images(val_images, val_images_dir, val_labels_dir)
        process_images(test_images, test_images_dir, test_labels_dir)

        # Generate the YAML configuration file
        yaml_content = {
            'train': str(train_images_dir),
            'val': str(val_images_dir),
            'test': str(test_images_dir),
            'nc': 2,  # Number of classes
            'names': ['Dirty', 'Fair']
        }

        with open(base_dir / 'dataset_config.yaml', 'w') as yaml_file:
            yaml.dump(yaml_content, yaml_file)

        self.stdout.write(self.style.SUCCESS('Successfully generated YOLOv8 dataset and configuration file'))
