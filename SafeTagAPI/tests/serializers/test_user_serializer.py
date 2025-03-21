import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from SafeTagAPI.serializers.user_serializer import UsersSerializer
from SafeTagAPI.models.user_model import CustomUser

@pytest.mark.django_db
class TestUsersSerializer:

    def test_user_serializer_valid_data(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        serializer = UsersSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'testuser@example.com'
        assert user.check_password('testpassword123')
        assert user.username is not None  # Vérifie que le username est rempli
        assert user.username != '' 

    def test_user_serializer_invalid_data(self):
        data = {
            'email': 'invalidemail',
            'password': '123'
        }
        serializer = UsersSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_user_serializer_missing_password(self):
        data = {
            'email': 'testuser@example.com'
        }
        serializer = UsersSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_user_serializer_short_password(self):
        data = {
            'email': 'testuser@example.com',
            'password': '123'
        }
        serializer = UsersSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        
    def test_user_serializer_auto_username(self):
        data = {
            'email': 'testuser2@example.com',
            'password': 'testpassword123'
        }
        serializer = UsersSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username is not None  # Vérifie que le username est rempli
        assert user.username != ''  # Vérifie que le username n'est pas vide
        assert CustomUser.objects.filter(username=user.username).exists()
        
    def test_obtain_jwt_token(self):
        client = APIClient()
        user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword123')
        url = reverse('token_obtain_pair')
        print(user.username)
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = client.post(url, data, format='json')
        if response.status_code != 200:
            print(response.data)
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.status_code == 200

    def test_refresh_jwt_token(self):
        client = APIClient()
        user = CustomUser.objects.create_user(email='testuser@example.com', password='testpassword123')
        url = reverse('token_obtain_pair')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = client.post(url, data, format='json')
        if response.status_code != 200:
            print(response.data)
            print('access' in response.data)
            print('refresh' in response.data)
        assert response.status_code == 200
        refresh_token = response.data['refresh']

        url = reverse('token_refresh')
        data2 = {
            'refresh': refresh_token
        }
        print(user)
        response2 = client.post(url, data2, format='json')
        print(response2.data)
        assert response2.status_code == 200
        assert 'access' in response.data