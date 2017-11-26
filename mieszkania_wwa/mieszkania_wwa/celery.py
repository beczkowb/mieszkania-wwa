import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
from offers.tasks import OfferRefresher

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mieszkania_wwa.settings')

app = Celery('mieszkania_wwa', broker='redis://localhost')


@app.task
def refresh_offers():
    print('refresh started')
    OfferRefresher.instance().refresh()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.add_periodic_task(30.0, refresh_offers, name='refresh 30')

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


