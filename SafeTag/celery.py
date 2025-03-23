from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Définir le module de configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SafeTag.settings')

app = Celery('SafeTag')

# Utiliser la configuration de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir les tâches définies dans les applications Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')