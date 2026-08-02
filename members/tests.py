from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
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

    def test_download_calendar_returns_ics_content(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Test Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'A test event',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/calendar', response['Content-Type'])
        self.assertIn('BEGIN:VCALENDAR', response.content.decode('utf-8'))
        self.assertIn('SUMMARY:Test Event', response.content.decode('utf-8'))

    def test_download_calendar_preserves_multiline_details(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Test Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'First line\nSecond line\nThird line',
            },
        )

        content = response.content.decode('utf-8')

        self.assertIn('DESCRIPTION:First line\\nSecond line\\nThird line', content)

    def test_download_calendar_preserves_crlf_multiline_details(self):
        response = self.client.get(
            reverse('download_calendar'),
            {
                'title': 'Test Event',
                'date': '2026-08-02',
                'location': 'Bern',
                'details': 'First line\r\nSecond line\r\nThird line',
            },
        )

        content = response.content.decode('utf-8')

        self.assertIn('DESCRIPTION:First line\\nSecond line\\nThird line', content)
        self.assertNotIn('DESCRIPTION:First line\r', content)
