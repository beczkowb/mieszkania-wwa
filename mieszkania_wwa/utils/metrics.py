from django.db import models
from django.utils import timezone


class MetricModel(models.Model):
    name = models.CharField(max_length=100)
    count = models.BigIntegerField()
    timestamp = models.DateTimeField()


class MetricReporter:
    @staticmethod
    def meter(name):
        MetricModel.objects.create(name=name, count=1, timestamp=timezone.now())

    @classmethod
    def metered_view(cls, view):
        def decorated_view(request):
            cls.meter(f'views.{view.__name__}')
            return view(request)
        return decorated_view