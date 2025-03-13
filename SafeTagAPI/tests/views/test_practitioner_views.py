import os
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from SafeTagAPI.models.practitioner_model import Practitioner, Address, Organization
from SafeTagAPI.models.review_model import Review
from unittest.mock import patch
import json
from asgiref.sync import sync_to_async

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.django_db
class PractitionerAsyncViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    @patch('SafeTagAPI.views.practitioner_views.get_all_practitioners')
    def test_get_practitioners(self, mock_get_all_practitioners):
        mock_get_all_practitioners.return_value = ([], None)
        response = self.client.get('/practitioner/async-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'practitioners': [], 'next_page_url': None})

    @pytest.mark.asyncio
    @patch('SafeTagAPI.views.practitioner_views.get_practitioner_details')
    async def test_post_practitioner(self, mock_get_practitioner_details):
        mock_get_practitioner_details.return_value = {
            'name': 'John',
            'surname': 'Doe',
            'api_id': 123,
            'reimboursement_sector': None,
            'organizations': [{'api_organization_id':1,'name':"Orga123","addresses":[{
                "line":"123 Main St",
                "city":"Test City",
                "department":10,
                "latitude":12.34,
                "longitude":56.78,
                "wheelchair_accessibility":None,
                "is_active":True
            }]}]
        }
        response = await sync_to_async(self.client.post)(
            '/practitioner/async-list/',
            data=json.dumps({'api_id': 123}),
            content_type='application/json'
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print("Validation errors:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], 'John')

class PractitionerViewSetTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.practitioner = Practitioner.objects.create(name="John", surname="Doe",api_id=1)

    def test_retrieve_practitioner(self):
        response = self.client.get(f'/practitioner/{self.practitioner.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'John')

    @patch('SafeTagAPI.models.practitioner_model.Practitioner.get_tag_averages')
    def test_retrieve_practitioner_with_tags(self, mock_get_tag_averages):
        mock_get_tag_averages.return_value = []
        response = self.client.get(f'/practitioner/{self.practitioner.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tag_summary_list', response.json())

    def test_practitioner_reviews(self):
        review = Review.objects.create(
            review_date="2023-01-01",
            comment="Test Comment",
            id_user_id=1,
            id_practitioner=self.practitioner,
            id_address_id=1
        )
        response = self.client.get(f'/practitioner/{self.practitioner.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

class AddressViewSetTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.address = Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=1,
            latitude=12.34,
            longitude=56.78,
            wheelchair_accessibility=True,
            is_active=True
        )

    def test_update_wheelchair_accessibility(self):
        response = self.client.patch(
            f'/address/{self.address.id}/',
            data=json.dumps({'wheelchair_accessibility': False}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['wheelchair_accessibility'], False)

    def test_update_invalid_field(self):
        response = self.client.patch(
            f'/address/{self.address.id}/',
            data=json.dumps({'city': 'New City'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Only wheelchair_accessibility can be updated.')

class OrganizationViewSetTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.organization = Organization.objects.create(name="Test Organization")

    def test_retrieve_organization(self):
        response = self.client.get(f'/organization/{self.organization.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'Test Organization')