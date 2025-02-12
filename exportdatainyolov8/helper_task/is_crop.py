import cv2
import os
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def crop(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image):
    """
    Black out half of all bounding box areas in the same image and adjust the bounding box dimensions.
    :param image_counter: Counter for unique image naming.
    :param unique_image_name: Unique name for the image.
    :param images_dir: Directory to save images.
    :param img_np: Image as a NumPy array.
    :param labels_dir: Directory to save labels.
    :param labels: List of bounding box labels.
    :param classes: List of class names.
    :param cat_image: Object with image properties like width and height.
    """
    modified_img = img_np.copy()  # Make a copy to apply changes

    new_labels = []  # To store the adjusted bounding box data for YOLO labels

    for label in labels:
        class_id = classes.index(label.label)  # Get the class ID dynamically

        # Calculate original bounding box coordinates
        x_min = int(label.x)
        y_min = int(label.y)
        x_max = int(label.x + label.width)
        y_max = int(label.y + label.height)

        # Determine the region to black out (left half)
        black_x_min = x_min
        black_x_max = x_min + (x_max - x_min) // 2
        black_y_min = y_min
        black_y_max = y_max

        # Apply the blackout
        modified_img[black_y_min:black_y_max, black_x_min:black_x_max] = 0

        # Adjust the bounding box to the remaining visible half
        new_x = black_x_max
        new_y = y_min
        new_width = x_max - black_x_max
        new_height = y_max - y_min

        # Normalize the new bounding box dimensions relative to the image size
        x_center = (new_x + new_width / 2) / cat_image.image_width
        y_center = (new_y + new_height / 2) / cat_image.image_height
        width = new_width / cat_image.image_width
        height = new_height / cat_image.image_height

        # Append new label to the list
        new_labels.append(f'{class_id} {x_center} {y_center} {width} {height}')

    # Save the modified image
    modified_image_name = f"blackout_{image_counter}_{unique_image_name}.jpg"
    modified_image_path = os.path.join(images_dir, modified_image_name)
    cv2.imwrite(modified_image_path, modified_img)

    # Write all the new labels in YOLO format
    modified_label_path = os.path.join(labels_dir, f'{os.path.splitext(modified_image_name)[0]}.txt')
    with open(modified_label_path, 'w') as f:
        f.write('\n'.join(new_labels))
        logger.info(f'Modified labels written for image {unique_image_name}.')

    logger.info(f'Processed image {unique_image_name} with all bounding boxes blacked out.')
