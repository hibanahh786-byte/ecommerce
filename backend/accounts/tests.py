from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User

class AccountsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auth:auth_register')
        self.login_url = reverse('auth:auth_login')
        self.logout_url = reverse('auth:auth_logout')
        self.users_url = reverse('users:user_list')
        self.profile_url = reverse('users:user_profile')

        self.user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='TestPassword123',
            full_name='Regular User',
            role=User.Role.USER
        )

        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='AdminPassword123',
            full_name='Admin User',
            role=User.Role.ADMIN,
            is_staff=True
        )

    def test_user_registration_success(self):
        payload = {
            "full_name": "New Person",
            "username": "newperson",
            "email": "new@example.com",
            "password": "Password123",
            "confirm_password": "Password123"
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user']['role'], 'USER')

    def test_registration_password_mismatch(self):
        payload = {
            "full_name": "Mismatch Person",
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": "Password123",
            "confirm_password": "DifferentPassword123"
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        payload = {
            "full_name": "Dup Email",
            "username": "dupemail",
            "email": "regular@example.com", # already exists
            "password": "Password123",
            "confirm_password": "Password123"
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        res = self.client.post(self.login_url, {
            "username_or_email": "regular@example.com",
            "password": "TestPassword123"
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.data['user']['role'], 'USER')

    def test_admin_list_users_permission(self):
        # Regular user should be rejected (403)
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.users_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user should succeed
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(self.users_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 2)

    def test_user_profile_update(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.put(self.profile_url, {
            "full_name": "Updated Regular User",
            "email": "updated_regular@example.com"
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Regular User")
