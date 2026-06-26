from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/auth/profile/'
        self.check_phone_url = '/api/auth/check-phone/'
        self.reset_password_url = '/api/auth/reset-password/'

    # --- Register Tests ---
    def test_register_success(self):
        res = self.client.post(self.register_url, {
            "name": "Test User",
            "phone_number": "9876543210",
            "password": "test123",
            "confirm_password": "test123"
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', res.data)

    def test_register_duplicate_phone(self):
        User.objects.create_user(phone_number="9876543210", name="Existing", password="test123")
        res = self.client.post(self.register_url, {
            "name": "Test User",
            "phone_number": "9876543210",
            "password": "test123",
            "confirm_password": "test123"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        res = self.client.post(self.register_url, {
            "name": "Test User",
            "phone_number": "9876543210",
            "password": "test123",
            "confirm_password": "wrong123"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_phone(self):
        res = self.client.post(self.register_url, {
            "name": "Test User",
            "phone_number": "123",
            "password": "test123",
            "confirm_password": "test123"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Login Tests ---
    def test_login_success(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        res = self.client.post(self.login_url, {
            "phone_number": "9876543210",
            "password": "test123"
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_login_wrong_password(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        res = self.client.post(self.login_url, {
            "phone_number": "9876543210",
            "password": "wrongpassword"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_phone(self):
        res = self.client.post(self.login_url, {
            "phone_number": "0000000000",
            "password": "test123"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Profile Tests ---
    def test_profile_with_token(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        login = self.client.post(self.login_url, {
            "phone_number": "9876543210",
            "password": "test123"
        })
        token = login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_profile_without_token(self):
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Check Phone Tests ---
    def test_check_phone_exists(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        res = self.client.post(self.check_phone_url, {"phone_number": "9876543210"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('reset_token', res.data)

    def test_check_phone_not_exists(self):
        res = self.client.post(self.check_phone_url, {"phone_number": "0000000000"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Reset Password Tests ---
    def test_reset_password_success(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        # Get reset token
        check = self.client.post(self.check_phone_url, {"phone_number": "9876543210"})
        reset_token = check.data['reset_token']
        # Reset password
        res = self.client.post(self.reset_password_url, {
            "reset_token": reset_token,
            "phone_number": "9876543210",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reset_password_invalid_token(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        res = self.client.post(self.reset_password_url, {
            "reset_token": "invalidtoken",
            "phone_number": "9876543210",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_token_phone_mismatch(self):
        User.objects.create_user(phone_number="9876543210", name="Test", password="test123")
        User.objects.create_user(phone_number="9999999999", name="Other", password="test123")
        # Get token for first user
        check = self.client.post(self.check_phone_url, {"phone_number": "9876543210"})
        reset_token = check.data['reset_token']
        # Try to reset second user's password with first user's token
        res = self.client.post(self.reset_password_url, {
            "reset_token": reset_token,
            "phone_number": "9999999999",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)