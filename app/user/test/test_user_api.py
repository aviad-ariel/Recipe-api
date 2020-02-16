from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


def create_payload(**kwargs):
    return kwargs


class PublicUserAPITests(TestCase):
    """Test users public API endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_create_vaild_user_success(self):
        """Test creating user with vaild payload is successful"""
        payload = create_payload(
            email='test@test.com',
            password='testpass',
            name='Test Name'
        )
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""
        payload = create_payload(email='test@test.com', password='testpass')
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length(self):
        """Test that password is not too short (>5)"""
        payload = create_payload(email='test@test.com', password='sr')
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user)

    def test_create_token_for_user(self):
        """Test to check token creation"""
        payload = create_payload(email='test@test.com', password='testpass')
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_invaild_credentials(self):
        """Test that token is not created for worng credentials"""
        create_user(email='test@test.com', password='testpassword')
        payload = create_payload(email='test@test.com', password='WorngPass')
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_user_does_not_exist(self):
        """Test that token is not created for not exist user"""
        payload = create_payload(email='test@test.com', password='testpass')
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_missings_fields(self):
        """Test that all fields exist"""
        payload = create_payload(email='test@test.com', password='')
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrive_user_unauthorized(self):
        """Test that authentication is required for user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """Test user private API endpoints"""

    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpassword",
            name="Test User"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retreving profile for authenticated user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': 'test@test.com',
            'name': 'Test User'
        })

    def test_post_not_allowed_on_me_endpoint(self):
        """Test that post requset is not allowed on the me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update user profile for authenticated user"""
        payload = create_payload(name='Test Newname', password='newpassword')
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
