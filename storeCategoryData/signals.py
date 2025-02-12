from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ImageLabel, CategoryImage
from StoreLabelData.models import Label

print("Signals module for storeCategoryData is loaded")

@receiver(pre_save, sender=Label)
def sync_labels_pre_save(sender, instance, **kwargs):
    # print(f"Pre-save signal triggered for Label: {instance}")
    # print(instance.image)
    #
    # try:
    #     # Ensure the corresponding CategoryImage exists
    #     category_image = CategoryImage.objects.get(image=instance.image)
    #     print(f"Found CategoryImage: {category_image}")
    # except CategoryImage.DoesNotExist:
    #     print(f"No CategoryImage found for Image: {instance.image}")
    #     return  # Exit if no related CategoryImage

    try:
        image_labels = ImageLabel.objects.filter(label_id=instance.label_id)
        

        if image_labels.exists():
            # Update each matching ImageLabel
            for image_label in image_labels:
                print(f"Found existing ImageLabel: {image_label}")

                # Update the ImageLabel attributes
                image_label.x = instance.x
                image_label.y = instance.y
                image_label.width = instance.width
                image_label.height = instance.height
                image_label.label_id = instance.label_id
                image_label.save()
                print(f"Updated ImageLabel: {image_label}")
    except ImageLabel.DoesNotExist:
        # Handle cases where no matching ImageLabel is found
        print(f"No matching ImageLabel found for label_id: {instance.label_id}")




        return

    # Find the single CategoryImage object linked to the Image of this Label


    # Update the corresponding ImageLabel for the CategoryImage

