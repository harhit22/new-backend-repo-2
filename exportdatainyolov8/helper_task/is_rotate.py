import cv2
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def rotate(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image):
    rotated_image_name = f"rotated_{image_counter}_{unique_image_name}"
    rotated_image_path = os.path.join(images_dir, rotated_image_name)
    img_rotated = cv2.rotate(img_np, cv2.ROTATE_180)
    img_rotated_rgb = cv2.cvtColor(img_rotated, cv2.COLOR_BGR2RGB)
    cv2.imwrite(rotated_image_path, img_rotated_rgb)

    # Save the same labels for the blurred image, adjusting the bounding boxes
    rotated_image_path = os.path.join(labels_dir, f'{os.path.splitext(rotated_image_name)[0]}.txt')
    with open(rotated_image_path, 'w') as f:
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
            new_x_center = 1 - x_center  # Flip horizontally
            new_y_center = 1 - y_center
            width = label.width / cat_image.image_width
            height = label.height / cat_image.image_height

            # Apply resizing adjustments to the bounding box
            x_center = new_x_center * 640  # Resize the center to 640x640
            y_center = new_y_center * 640  # Resize the center to 640x640
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
