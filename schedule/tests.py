from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import ProgramSchedule
from .serializers import ProgramScheduleSerializer

class ScheduleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.schedule_url = '/api/schedule/'
        ProgramSchedule.objects.all().delete()

    def test_get_schedule(self):
        ProgramSchedule.objects.create(
            day='MON', start_time='08:00', end_time='10:00',
            title='Morning Show', rj='Rajesh'
        )
        res = self.client.get(self.schedule_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Paginated response has results nested under 'results' key
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(len(res.data['results']), 1)

    def test_schedule_day_order(self):
        ProgramSchedule.objects.create(
            day='FRI', start_time='08:00', end_time='10:00',
            title='Friday Show', rj='RJ1'
        )
        ProgramSchedule.objects.create(
            day='MON', start_time='08:00', end_time='10:00',
            title='Monday Show', rj='RJ2'
        )
        res = self.client.get(self.schedule_url)
        # Extract days from the paginated results list
        days = [item['day'] for item in res.data['results']]
        self.assertEqual(days[0], 'MON')
        self.assertEqual(days[1], 'FRI')

    def test_end_time_before_start_time(self):
        serializer = ProgramScheduleSerializer(data={
            'day': 'MON',
            'start_time': '10:00',
            'end_time': '09:00',
            'title': 'Test',
            'rj': 'RJ'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)