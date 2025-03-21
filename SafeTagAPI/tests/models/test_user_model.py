from django.test import TestCase
from SafeTagAPI.models.user_model import CustomUser

class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="password123"
        )

    def test_user_creation(self):
        user = CustomUser.objects.get(email="testuser@example.com")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_user_str(self):
        user = CustomUser.objects.get(email="testuser@example.com")
        self.assertEqual(str(user), f"{user.username}-{user.email}")