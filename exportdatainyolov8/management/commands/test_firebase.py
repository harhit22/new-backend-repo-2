from django.core.management.base import BaseCommand
from cinx_backend.firebase import bucket  # Import the bucket from your firebase.py

class Command(BaseCommand):
    help = 'Test Firebase Storage connection'

    def handle(self, *args, **kwargs):
        try:
            # List files in the root of the Firebase Storage bucket
            blobs = bucket.list_blobs()
            print("Connected to Firebase Storage successfully!")
            print("Files in the bucket:")
            for blob in blobs:
                print(blob.name)
        except Exception as e:
            print(f"Error connecting to Firebase Storage: {e}")
