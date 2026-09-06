from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, UserRole, Brand, Organization

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name='Test Org', slug='test-org')
        self.brand = Brand.objects.create(organization=self.org, name='Test Brand', slug='test-brand')

        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User',
            role=UserRole.BRAND_OWNER,
            brand=self.brand
        )

    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'email': 'testuser@example.com',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['user']['role'], UserRole.BRAND_OWNER)

    def test_login_invalid_password(self):
        response = self.client.post('/api/auth/login/', {
            'email': 'testuser@example.com',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_current_user_me(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertEqual(response.data['role'], UserRole.BRAND_OWNER)
