from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinx_backend.settings')

app = Celery('cinx_backend')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings, namespace='CELERY')

app.conf.update(
    broker_url='redis://localhost:6379/0',  # Redis as broker
    result_backend='redis://localhost:6379/0',  # Redis as result backend
)
# beat setting

app.autodiscover_tasks()
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
