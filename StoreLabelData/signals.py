from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Image, Label
from django.core.exceptions import ValidationError
import time

@receiver(pre_save, sender=Image)
def prevent_duplicate_images(sender, instance, **kwargs):
    """
    Signal to check for duplicate images before saving.
    """
    # Simulating delay for race condition testing
    #time.sleep(0.1)  # 500ms delay

    if Image.objects.filter(
        firebase_url=instance.firebase_url,
        project=instance.project,
    ).exists():
       # raise ValidationError("An image with this firebase_url and project already exists.")
       pass
@receiver(post_save, sender=Image)
def handle_duplicate_images(sender, instance, **kwargs):
    """
    Signal to remove duplicates after saving an image.
    """
    # Check for duplicates with the same firebase_url and project
    duplicates = Image.objects.filter(
        firebase_url=instance.firebase_url,
        project=instance.project,
    ).exclude(id=instance.id)

    # If duplicates are found, delete the most recent one (keep the oldest)
    if duplicates.exists():
        # Sort duplicates by ID and delete the latest
        duplicates.latest('id').delete()


@receiver(post_save, sender=Label)
def remove_duplicate_labels(sender, instance, **kwargs):
    """
    Signal to remove duplicate labels after saving.
    """
    # Find all labels with the same attributes, excluding the current instance
    duplicates = Label.objects.filter(
        image=instance.image,
        x=instance.x,
        y=instance.y,
        width=instance.width,
        height=instance.height,
    ).exclude(id=instance.id)

    # Delete duplicates if any exist
    if duplicates.exists():
        duplicates.delete()

