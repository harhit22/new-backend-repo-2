import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("./wevois-label-project-firebase-adminsdk-oxhfm-726700b24c.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'wevois-dev.appspot.com'
})

bucket = storage.bucket()
