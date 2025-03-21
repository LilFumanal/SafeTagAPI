import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from SafeTagAPI.models.user_model import CustomUser

class UserCreateViewTests(APITestCase):
    def test_create_user(self):
        url = reverse('register')
        data = {
            'password': 'testpassword123',
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        
class CustomTokenObtainPairViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            password='testpassword123',
            email='testuser@example.com'
        )

    def test_obtain_token(self):
        url = reverse('token_obtain_pair')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        print(response)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class CustomTokenRefreshViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            password='testpassword123',
            email='testuser@example.com'
        )
        url = reverse('token_obtain_pair')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.refresh_token = response.data['refresh']

    def test_refresh_token(self):
        url = reverse('token_refresh')
        data = {
            'refresh': self.refresh_token
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)