import cv2
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def adjust_brightness(img, factor):
    """
        Adjust the brightness of an image.
        :param img: Input image as a NumPy array.
        :param factor: Brightness adjustment factor (e.g., 1.1 for 10% brighter, 0.9 for 10% dimmer).
        :return: Brightness-adjusted image.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, int((factor - 1) * 255))
    v = cv2.min(v, 255)
    hsc_adjusted = cv2.merge((h, s, v))
    return cv2.cvtColor(hsc_adjusted, cv2.COLOR_HSV2BGR)


def bright_image(image_counter, unique_image_name, images_dir, img_np, labels_dir, labels, classes, cat_image):
    """
    Process the image to generate blurred, brighter, and dimmer versions with saved labels.
    """

    variations = [
        ("brighter", lambda img: adjust_brightness(img, 1.1)),  # 10% brighter
        ("dimmer", lambda img: adjust_brightness(img, 0.9))  # 10% dimmer
    ]

    for variation_name, variation_function in variations:
        variation_image_name = f"{variation_name}_{image_counter}_{unique_image_name}"
        variation_image_path = os.path.join(images_dir, variation_image_name)

        # Generate variation
        ima_variation = variation_function(img_np)
        cv2.imwrite(variation_image_path, ima_variation)  # Corrected variable name

        # Save the same labels for the transformed image
        variation_label_path = os.path.join(labels_dir, f'{os.path.splitext(variation_image_name)[0]}.txt')
        with open(variation_label_path, 'w') as f:
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
                logger.info(f'{variation_name} label written: {class_id} {x_center} {y_center} {width} {height}')

    logger.info(f'Processed image {unique_image_name} with variations saved.')



