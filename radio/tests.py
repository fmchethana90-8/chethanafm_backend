from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import LiveProgram

class RadioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.live_url = '/api/live/'

    def test_get_live_program(self):
        LiveProgram.objects.create(
            title="Morning Show",
            rj="Rajesh",
            is_live=True,
            stream_url="https://radio.chethanafm.com/live"
        )
        res = self.client.get(self.live_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('title', res.data)
        self.assertIn('stream_url', res.data)