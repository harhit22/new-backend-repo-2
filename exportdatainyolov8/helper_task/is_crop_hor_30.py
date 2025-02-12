import cv2
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def crop_hor_30(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image):
    """
    Black out 30% of the image horizontally (top or bottom) and adjust bounding box dimensions.
    :param image_counter: Counter for unique image naming.
    :param unique_image_name: Unique name for the image.
    :param images_dir: Directory to save images.
    :param img_np: Image as a NumPy array.
    :param labels_dir: Directory to save labels.
    :param labels: List of bounding box labels.
    :param classes: List of class names.
    :param cat_image: Object with image properties like width and height.
    """
    modified_img = img_np.copy()  # Make a copy of the image

    # Determine the blackout region (top 30%)
    blackout_height = int(cat_image.image_height * 0.3)
    modified_img[:blackout_height, :] = 0  # Apply blackout to the top 30%

    new_labels = []  # To store adjusted bounding box data

    for label in labels:
        class_id = classes.index(label.label)  # Get class ID dynamically

        # Calculate original bounding box coordinates
        x_min = int(label.x)
        y_min = int(label.y)
        x_max = int(label.x + label.width)
        y_max = int(label.y + label.height)

        # Adjust bounding boxes if they intersect with the blackout region
        if y_min < blackout_height:
            # Clip the top of the bounding box to start at the blackout boundary
            y_min = blackout_height
            new_height = y_max - y_min
        else:
            new_height = y_max - y_min

        new_y = y_min
        new_width = x_max - x_min
        new_x = x_min

        # Normalize bounding box for YOLO format
        x_center = (new_x + new_width / 2) / cat_image.image_width
        y_center = (new_y + new_height / 2) / cat_image.image_height
        width = new_width / cat_image.image_width
        height = new_height / cat_image.image_height

        new_labels.append(f'{class_id} {x_center} {y_center} {width} {height}')

    # Save the modified image
    modified_image_name = f"blackout_top_30_{image_counter}_{unique_image_name}.jpg"
    modified_image_path = os.path.join(images_dir, modified_image_name)
    cv2.imwrite(modified_image_path, modified_img)

    # Save updated labels in YOLO format
    modified_label_path = os.path.join(labels_dir, f'{os.path.splitext(modified_image_name)[0]}.txt')
    with open(modified_label_path, 'w') as f:
        f.write('\n'.join(new_labels))
        logger.info(f'Modified labels written for image {unique_image_name}.')

    logger.info(f'Processed image {unique_image_name} with top 30% blacked out.')
