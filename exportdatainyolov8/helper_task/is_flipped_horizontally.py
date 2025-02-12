import cv2
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def flipped_horizontally(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image):
    flipped_image_name = f"flipped_{image_counter}_{unique_image_name}"
    flipped_image_path = os.path.join(images_dir, flipped_image_name)

    # Flip the image horizontally
    img_flipped = cv2.flip(img_np, 1)  # 1 means horizontal flip
    img_flipped_rgb = cv2.cvtColor(img_flipped, cv2.COLOR_BGR2RGB)
    cv2.imwrite(flipped_image_path, img_flipped_rgb)

    # Save the same labels for the flipped image, adjusting the bounding boxes
    flipped_label_path = os.path.join(labels_dir, f'{os.path.splitext(flipped_image_name)[0]}.txt')
    with open(flipped_label_path, 'w') as f:
        for label in labels:
            class_id = classes.index(label.label)  # Get the class ID dynamically

            # Normalize the bounding box coordinates to YOLO format
            x_center = (label.x + label.width / 2) / cat_image.image_width
            y_center = (label.y + label.height / 2) / cat_image.image_height
            width = label.width / cat_image.image_width
            height = label.height / cat_image.image_height

            # Flip the x_center horizontally
            new_x_center = 1 - x_center  # Horizontal flip

            # Normalize bounding box for YOLO format (optional for resizing)
            x_center = new_x_center * 640  # Resize the center to 640x640
            y_center = y_center * 640  # Keep y_center as it is
            width = width * 640  # Resize width
            height = height * 640  # Resize height

            # Normalize back to YOLO values
            x_center /= 640
            y_center /= 640
            width /= 640
            height /= 640

            # Write the label in YOLO format
            f.write(f'{class_id} {x_center} {y_center} {width} {height}\n')
            logger.info(f'Label written (flipped): {class_id} {x_center} {y_center} {width} {height}')
