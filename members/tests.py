from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import sj_events
from .sj_utils import get_event_info


class EventInfoTests(TestCase):
    def test_get_event_info_includes_location(self):
        sj_events.objects.create(
            event_name='Test Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_location='Berlin',
        )

        event_info = get_event_info()

        self.assertEqual(event_info['location'], 'Berlin')
