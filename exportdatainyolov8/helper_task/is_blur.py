import cv2
import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
def blur(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image):
    blurred_image_name = f"blurred_{image_counter}_{unique_image_name}"
    blurred_image_path = os.path.join(images_dir, blurred_image_name)
    img_blurred = cv2.GaussianBlur(img_np, (5, 5), 0)
    img_blurred_rgb = cv2.cvtColor(img_blurred, cv2.COLOR_BGR2RGB)
    cv2.imwrite(blurred_image_path, img_blurred_rgb)

    # Save the same labels for the blurred image, adjusting the bounding boxes
    blurred_label_path = os.path.join(labels_dir, f'{os.path.splitext(blurred_image_name)[0]}.txt')
    with open(blurred_label_path, 'w') as f:
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
            height = height * 640  # Resize the height to 640x640

            # Normalize values for YOLO format
            x_center /= 640
            y_center /= 640
            width /= 640
            height /= 640

            # Write the label in YOLO format
            f.write(f'{class_id} {x_center} {y_center} {width} {height}\n')
            logger.info(f'Label written: {class_id} {x_center} {y_center} {width} {height}')
