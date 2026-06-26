from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import NotificationLog

User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/send-notification/'
        NotificationLog.objects.all().delete()

        # No 'username' — manager only takes phone_number, name, password
        self.admin = User.objects.create_superuser(
            phone_number='9999999999',
            name='Admin User',
            password='adminpass'
        )
        self.user = User.objects.create_user(
            phone_number='8888888888',
            name='Regular User',
            password='userpass'
        )

    # --- Permission Tests ---

    def test_unauthenticated_cannot_send(self):
        res = self.client.post(self.url, {'title': 'Hi', 'body': 'Test'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_cannot_send(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url, {'title': 'Hi', 'body': 'Test'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # --- Success Tests ---

    @patch('notifications.views.send_push_notification')
    def test_admin_can_send_notification(self, mock_send):
        mock_send.return_value = 'message-id-123'
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(self.url, {'title': 'Hello', 'body': 'World'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'sent')

    @patch('notifications.views.send_push_notification')
    def test_notification_is_logged_on_success(self, mock_send):
        mock_send.return_value = 'message-id-123'
        self.client.force_authenticate(user=self.admin)
        self.client.post(self.url, {'title': 'Log Test', 'body': 'Check log'})
        self.assertEqual(NotificationLog.objects.count(), 1)
        log = NotificationLog.objects.first()
        self.assertEqual(log.title, 'Log Test')
        self.assertEqual(log.body, 'Check log')

    # --- Firebase Failure Tests ---

    @patch('notifications.views.send_push_notification')
    def test_firebase_failure_returns_500(self, mock_send):
        mock_send.side_effect = Exception('Firebase unreachable')
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(self.url, {'title': 'Fail', 'body': 'Test'})
        self.assertEqual(res.status_code, 500)
        self.assertEqual(res.data['status'], 'failed')
        self.assertIn('Firebase unreachable', res.data['error'])

    @patch('notifications.views.send_push_notification')
    def test_notification_is_logged_even_on_firebase_failure(self, mock_send):
        mock_send.side_effect = Exception('Firebase unreachable')
        self.client.force_authenticate(user=self.admin)
        self.client.post(self.url, {'title': 'Fail Log', 'body': 'Still logs'})
        self.assertEqual(NotificationLog.objects.count(), 1)

    # --- Validation Tests ---

    @patch('notifications.views.send_push_notification')
    def test_missing_title_returns_400(self, mock_send):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(self.url, {'body': 'No title here'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data)

    @patch('notifications.views.send_push_notification')
    def test_missing_body_returns_400(self, mock_send):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(self.url, {'title': 'No body here'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('body', res.data)

    @patch('notifications.views.send_push_notification')
    def test_title_exceeds_max_length(self, mock_send):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(self.url, {'title': 'A' * 101, 'body': 'Test'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data)

    # --- Model Tests ---

    def test_notification_log_str(self):
        log = NotificationLog.objects.create(title='Test Title', body='Test Body')
        self.assertEqual(str(log), 'Test Title')

    def test_notification_log_ordering(self):
        NotificationLog.objects.create(title='First', body='A')
        NotificationLog.objects.create(title='Second', body='B')
        logs = list(NotificationLog.objects.all())
        self.assertEqual(logs[0].title, 'Second')
        self.assertEqual(logs[1].title, 'First')