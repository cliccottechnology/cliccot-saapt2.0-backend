from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.profile_url = reverse('auth_profile')
        self.logout_url = reverse('auth_logout')

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
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], 'johndoe@example.com')
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
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

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
        reg_response = self.client.post(self.register_url, self.user_data, format='json')
        access_token = reg_response.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'johndoe')
