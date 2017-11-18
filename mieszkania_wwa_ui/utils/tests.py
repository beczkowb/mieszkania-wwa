from django.test import TestCase

from utils.metrics import MetricReporter, MetricModel


class ShouldMeterCall(TestCase):
    def test_should_meter_call(self):
        # given
        @MetricReporter.metered_view
        def function_to_meter(req):
            pass

        # when
        function_to_meter('req')

        # then
        self.assertEqual(MetricModel.objects.count(), 1)