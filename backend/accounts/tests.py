from django.urls import reverse
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, PasswordResetOTP

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.profile_url = reverse('auth_profile')
        self.logout_url = reverse('auth_logout')
        self.forgot_password_url = reverse('auth_forgot_password')
        self.verify_otp_url = reverse('auth_verify_otp')
        self.reset_password_url = reverse('auth_reset_password')
        self.forgot_password_ui_url = reverse('auth_forgot_password_ui')

        self.user_data = {
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        }

    def test_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "User registered successfully.")
        self.assertIn('user', response.data)
        self.assertNotIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'johndoe@example.com')
        self.assertEqual(response.data['user']['username'], 'johndoe')
        self.assertIn('created_at', response.data['user'])
        self.assertIn('updated_at', response.data['user'])
        self.assertTrue(CustomUser.objects.filter(email='johndoe@example.com').exists())

    def test_registration_password_mismatch(self):
        data = self.user_data.copy()
        data['confirm_password'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_login_with_username_success(self):
        # First register
        self.client.post(self.register_url, self.user_data, format='json')

        # Login using username
        login_payload = {
            'username_or_email': 'johndoe',
            'password': 'SecurePassword123!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Login successful.")
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['username'], 'johndoe')
        self.assertEqual(response.data['user']['email'], 'johndoe@example.com')
        self.assertNotIn('created_at', response.data['user'])

    def test_login_with_email_success(self):
        # First register
        self.client.post(self.register_url, self.user_data, format='json')

        # Login using email
        login_payload = {
            'username_or_email': 'johndoe@example.com',
            'password': 'SecurePassword123!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_login_invalid_password(self):
        self.client.post(self.register_url, self.user_data, format='json')

        login_payload = {
            'username_or_email': 'johndoe',
            'password': 'WrongPassword!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_profile_access(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_payload = {
            'username_or_email': 'johndoe',
            'password': 'SecurePassword123!',
        }
        login_res = self.client.post(self.login_url, login_payload, format='json')
        access_token = login_res.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'johndoe')

    def test_forgot_password_request_success(self):
        # Register user first
        self.client.post(self.register_url, self.user_data, format='json')

        response = self.client.post(
            self.forgot_password_url,
            {'email': 'johndoe@example.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "OTP has been sent to your registered email address.")
        self.assertEqual(response.data['email'], 'johndoe@example.com')

        # Check OTP created in DB
        otp_record = PasswordResetOTP.objects.filter(email='johndoe@example.com').first()
        self.assertIsNotNone(otp_record)
        self.assertEqual(len(otp_record.otp), 6)
        self.assertTrue(otp_record.is_valid())

        # Check mail was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password Reset OTP", mail.outbox[0].subject)
        self.assertIn(otp_record.otp, mail.outbox[0].body)

    def test_forgot_password_unregistered_email(self):
        response = self.client.post(
            self.forgot_password_url,
            {'email': 'nonexistent@example.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_verify_otp_success(self):
        self.client.post(self.register_url, self.user_data, format='json')
        self.client.post(self.forgot_password_url, {'email': 'johndoe@example.com'}, format='json')

        otp_record = PasswordResetOTP.objects.filter(email='johndoe@example.com').first()

        verify_payload = {
            'email': 'johndoe@example.com',
            'otp': otp_record.otp,
        }
        response = self.client.post(self.verify_otp_url, verify_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reset_token'], otp_record.reset_token)

        otp_record.refresh_from_db()
        self.assertTrue(otp_record.is_verified)

    def test_verify_otp_invalid_code(self):
        self.client.post(self.register_url, self.user_data, format='json')
        self.client.post(self.forgot_password_url, {'email': 'johndoe@example.com'}, format='json')

        verify_payload = {
            'email': 'johndoe@example.com',
            'otp': '999999',
        }
        response = self.client.post(self.verify_otp_url, verify_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data)

    def test_verify_otp_expired(self):
        self.client.post(self.register_url, self.user_data, format='json')
        self.client.post(self.forgot_password_url, {'email': 'johndoe@example.com'}, format='json')

        otp_record = PasswordResetOTP.objects.filter(email='johndoe@example.com').first()
        otp_record.expires_at = timezone.now() - timedelta(minutes=1)
        otp_record.save()

        verify_payload = {
            'email': 'johndoe@example.com',
            'otp': otp_record.otp,
        }
        response = self.client.post(self.verify_otp_url, verify_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data)

    def test_reset_password_full_flow_success(self):
        # 1. Register
        self.client.post(self.register_url, self.user_data, format='json')

        # 2. Request OTP
        self.client.post(self.forgot_password_url, {'email': 'johndoe@example.com'}, format='json')
        otp_record = PasswordResetOTP.objects.filter(email='johndoe@example.com').first()

        # 3. Verify OTP
        verify_res = self.client.post(
            self.verify_otp_url,
            {'email': 'johndoe@example.com', 'otp': otp_record.otp},
            format='json'
        )
        reset_token = verify_res.data['reset_token']

        # 4. Set New Password
        new_password = 'BrandNewPassword999!'
        reset_payload = {
            'email': 'johndoe@example.com',
            'reset_token': reset_token,
            'new_password': new_password,
            'confirm_password': new_password,
        }
        reset_res = self.client.post(self.reset_password_url, reset_payload, format='json')
        self.assertEqual(reset_res.status_code, status.HTTP_200_OK)
        self.assertEqual(reset_res.data['message'], "Password changed successfully. You can now log in with your new password.")

        # 5. Verify old password no longer works
        old_login = self.client.post(
            self.login_url,
            {'username_or_email': 'johndoe@example.com', 'password': 'SecurePassword123!'},
            format='json'
        )
        self.assertEqual(old_login.status_code, status.HTTP_400_BAD_REQUEST)

        # 6. Verify new password logs in successfully!
        new_login = self.client.post(
            self.login_url,
            {'username_or_email': 'johndoe@example.com', 'password': new_password},
            format='json'
        )
        self.assertEqual(new_login.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', new_login.data)

    def test_reset_password_mismatched_confirmation(self):
        self.client.post(self.register_url, self.user_data, format='json')
        self.client.post(self.forgot_password_url, {'email': 'johndoe@example.com'}, format='json')
        otp_record = PasswordResetOTP.objects.filter(email='johndoe@example.com').first()

        reset_payload = {
            'email': 'johndoe@example.com',
            'otp': otp_record.otp,
            'new_password': 'BrandNewPassword999!',
            'confirm_password': 'NotMatchingPassword123!',
        }
        response = self.client.post(self.reset_password_url, reset_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_reset_password_reusing_used_otp(self):
        self.client.post(self.register_url, self.user_data, format='json')
        self.client.post(self.forgot_password_url, {'email': 'johndoe@example.com'}, format='json')
        otp_record = PasswordResetOTP.objects.filter(email='johndoe@example.com').first()

        reset_payload = {
            'email': 'johndoe@example.com',
            'otp': otp_record.otp,
            'new_password': 'BrandNewPassword999!',
            'confirm_password': 'BrandNewPassword999!',
        }
        res1 = self.client.post(self.reset_password_url, reset_payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Re-attempt with same OTP
        reset_payload2 = {
            'email': 'johndoe@example.com',
            'otp': otp_record.otp,
            'new_password': 'AnotherNewPassword123!',
            'confirm_password': 'AnotherNewPassword123!',
        }
        res2 = self.client.post(self.reset_password_url, reset_payload2, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forgot_password_ui_view(self):
        response = self.client.get(self.forgot_password_ui_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"SAAPT - Forgot Password", response.content)

