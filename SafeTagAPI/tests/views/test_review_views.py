from datetime import date
import json
import os
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from SafeTagAPI.models.review_model import Review, Pathologie
from SafeTagAPI.models.tag_model import Review_Tag, Tag
from SafeTagAPI.models.practitioner_model import Address, Organization, Practitioner
from SafeTagAPI.models.user_model import CustomUser
from SafeTagAPI.serializers.review_serializer import ReviewSerializer
from SafeTagAPI.serializers.practitioner_serializer import PractitionerSerializer

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

class ReviewViewSetTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create(username='testuser', id=1)
        self.client.force_authenticate(user=self.user)
        self.practitioner = Practitioner.objects.create(name='John', surname='Doe', api_id="1")
        self.organization = Organization.objects.create(name="Test Organization", api_organization_id="1")
        self.address1 = Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=1,
            latitude=12.34,
            longitude=56.78,
            wheelchair_accessibility=True,
            is_active=True
        )
        self.address2 = Address.objects.create(
            line="456 Main St",
            city="TestTown",
            department=56,
            latitude=128.34,
            longitude=85.78,
            wheelchair_accessibility=False,
            is_active=True
        )
        self.organization.addresses.add(self.address1)
        self.organization.addresses.add(self.address2)
        self.practitioner.organizations.add(self.organization)
        self.pathologie = Pathologie.objects.create(name='TestPathologie1', description='Test Description')
        self.tag = Tag.objects.create(type='TestTag2', description='Test Description')
        self.review1 = Review.objects.create(
            id_practitioner=self.practitioner,
            id_user=self.user,
            id_address=self.address1,
            review_date="2025-03-23",
            comment="Excellent service"
        )
        self.review_data = {
            "api_practitioner_id": self.practitioner.api_id,
            "review_date": "2025-03-21",
            "comment": "Super!",
            "tags": [{"id_tag": self.tag.id, "rates": 5}],
            "pathologies": [{"id_pathologie": self.pathologie.id}],
            "id_address": self.address2.id,
            "id_user": self.user.id,
        }
    
    @pytest.mark.django_db
    def test_create_review(self):
        url = reverse("review-list")
        response = self.client.post(url, json.dumps(self.review_data), content_type="application/json")
        print(response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)
    
    @pytest.mark.django_db
    @patch("SafeTagAPI.lib.esante_api_treatement.get_practitioner_details")
    def test_create_review_fetch_practitioner_success(self, mock_get_practitioner_details):
        """
        Test création d'une review quand le praticien n'existe pas en base mais est trouvé via l'API.
        """
        # Simuler une réponse API valide
        mock_get_practitioner_details.return_value = {
            "api_id": "99999",
            "name": "Dr. API Test",
            "surname": "Jean",
            "organizations": [{"api_organization_id": 2, "name": "Test Organization", "addresses": [{"line": "123 Main St", "city": "Test City", "department": 1, "latitude": 12.34, "longitude": 56.78, "wheelchair_accessibility": True, "is_active": True}]}],
            "specialities": ["Cardiology"],
        }
        self.review_data["api_practitioner_id"] = "99999"
        url = reverse("review-list")
        response = self.client.post(url, json.dumps(self.review_data), content_type="application/json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Practitioner.objects.filter(api_id="99999").exists())
        self.assertEqual(Review.objects.count(), 2)

    @pytest.mark.django_db
    @patch("SafeTagAPI.lib.esante_api_treatement.get_practitioner_details")
    def test_create_review_fetch_practitioner_failure(self, mock_get_practitioner_details):
        """
        Test création d'une review quand le praticien n'existe pas et que l'API ne le trouve pas.
        """
        # Simuler une réponse API négative
        mock_get_practitioner_details.return_value = None

        self.review_data["api_practitioner_id"] = "fx006"  # Praticien inexistant
        url = reverse("review-list")
        response = self.client.post(url, json.dumps(self.review_data), content_type="application/json")

        # 🚫 Vérifications
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Practitioner.objects.filter(api_id="fx006").exists())  # Ne doit pas exister
        self.assertEqual(Review.objects.count(), 1)  # Aucune nouvelle review ne doit être ajoutée
