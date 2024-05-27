import os
from celery import Celery, platforms

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf.settings')

app = Celery('drf')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

platforms.C_FORCE_ROOT = True


# 配置了ignore_result忽略任务结果
# @app.task(bind=True, ignore_result=True)
@app.task(bind=True)
def debug_task(self, *args, **kwargs):
    print(f'Request: {self.request!r}')

    return args, kwargs
