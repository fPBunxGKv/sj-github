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

        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/calendar', response['Content-Type'])
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('SUMMARY:Test Event', content)
        self.assertIn('DTSTART:20260802T133000', content)
        self.assertIn('DTEND:20260802T180000', content)

    def test_download_calendar_uses_event_uuid_to_fetch_event_details(self):
        event = sj_events.objects.create(
            event_name='UUID Event',
            event_date=timezone.now().date() + timedelta(days=7),
            event_reg_start=timezone.now() - timedelta(days=1),
            event_reg_end=timezone.now() + timedelta(days=3),
            event_active=True,
            event_location='Zurich',
            event_program='Program line 1',
        )

        response = self.client.get(
            reverse('download_calendar'),
            {'event_uuid': str(event.uuid)},
        )

        content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('SUMMARY:UUID Event', content)
        self.assertIn('LOCATION:Zurich', content)
        self.assertIn('DESCRIPTION:Program line 1', content)

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
