import json
import os
from django.test import TestCase
from django.urls import reverse
from asgiref.sync import sync_to_async, async_to_sync
from httpx import AsyncClient
from rest_framework.test import APIClient
from unittest.mock import patch
import pytest
from rest_framework import status
from asgiref.sync import sync_to_async
from unittest.mock import patch, MagicMock
from django.test import AsyncClient
from SafeTagAPI.lib.esante_api_treatement import get_all_practitioners
from SafeTagAPI.models.practitioner_model import Address, Practitioner
from SafeTagAPI.models.review_model import Pathologie, Review, Review_Pathologie
from SafeTagAPI.models.tag_model import Review_Tag, Tag
from SafeTagAPI.models.user_model import CustomUser

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

class TestPractitionerAsyncViews:

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction = True)
    @patch('SafeTagAPI.views.practitioner_views.get_all_practitioners')
    async def test_get(self, mock_get_all_practitioners):
        client = AsyncClient()
        practitioners_data = ([], None)
        mock_get_all_practitioners.return_value = practitioners_data
        response = await client.get(reverse('practitioners'))
        assert response.status_code == 200
        assert response.json() == {'practitioners': [], 'next_page_url': None}
        
    @pytest.mark.asyncio
    @pytest.mark.django_db
    @patch('SafeTagAPI.views.practitioner_views.get_practitioner_details')
    async def test_post_with_valid_data(self, mock_get_practitioner_details):
        client = AsyncClient()
        practitioner_data = {
            "name": "John",
            "surname": "Doe",
            "specialities": ["Cardiology"],
            "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
            "organizations": [{
                "api_organization_id": 1,
                "name": "Organization",
                "addresses": [{
                    "line": "123 Main St",
                    "city": "Test City",
                    "department": 10,
                    "latitude": 12.34,
                    "longitude": 56.78,
                    "wheelchair_accessibility": True,
                    "is_active": True
                }]
            }],
            "api_id": 12345
        }
        mock_get_practitioner_details.return_value = practitioner_data

        response = await client.post(
            reverse('practitioners'),
            data=json.dumps({"api_id": 12345}),
            content_type='application/json'
        )
        assert response.status_code == 201
        assert response.json()['name'] == practitioner_data['name']
        assert response.json()['surname'] == practitioner_data['surname']

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_post_with_missing_api_id(self):
        client = AsyncClient()
        response = await client.post(
            reverse('practitioners'),
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert response.json() == {"error": "API ID is required to fetch practitioner details."}

    @pytest.mark.asyncio
    @pytest.mark.django_db
    @patch('SafeTagAPI.views.practitioner_views.get_practitioner_details')
    async def test_post_with_invalid_data(self, mock_get_practitioner_details):
        client = AsyncClient()
        mock_get_practitioner_details.return_value = None
        response = await client.post(
            reverse('practitioners'),
            data=json.dumps({"api_id": "invalid_id"}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert response.json() == {"error": "Failed to fetch practitioner details from the external API."}

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_patch(self):
        client = AsyncClient()
        practitioner = await sync_to_async(Practitioner.objects.create)(
            name="John",
            surname="Doe",
            specialities=["Cardiology"],
            api_id=12345
        )
        url = reverse('practitioners')
        data = {
            "api_id": 12345,
            "accessibilities": {"LSF": "Yes", "Visio": "Yes"}
        }
        response = await client.patch(url, data=json.dumps(data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['accessibilities'] == data['accessibilities']

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_patch_practitioner_not_found(self):
        client = AsyncClient()
        url = reverse('practitioners')
        data = {
            "api_id": 125,
            "accessibilities": {"LSF": "Yes", "Visio": "Yes"}
        }
        response = await client.patch(url, data=json.dumps(data), content_type='application/json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"error": "Practitioner not found"}


@pytest.mark.django_db
class TestPractitionerView:
    
    def test_retrieve_practitioner_found(self):
        client = APIClient()
        practitioner = Practitioner.objects.create(
            name="John",
            surname="Doe",
            specialities=["Cardiology"],
            api_id="12345"
        )
        url = reverse('practitioner-detail', args=[practitioner.id])
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == practitioner.name
        assert response.data['surname'] == practitioner.surname

    def test_retrieve_practitioner_not_found(self):
        client = APIClient()
        url = reverse('practitioner-detail', args=[999])
        response = client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "No Practitioner matches the given query."

    @patch('SafeTagAPI.models.practitioner_model.Practitioner.get_tag_averages')
    def test_retrieve_practitioner_with_tag_averages(self,mock_get_tag_averages):
        client = APIClient()
        practitioner = Practitioner.objects.create(
            name="John",
            surname="Doe",
            specialities=["Cardiology"],
            api_id="12345"
        )
        mock_get_tag_averages.return_value = {'tag1': 5, 'tag2': 3}
        url = reverse('practitioner-detail', args=[practitioner.id])
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == practitioner.name
        assert response.data['surname'] == practitioner.surname
        assert response.data['tag_summary_list'] == {'tag1': 5, 'tag2': 3}

    def test_practitioner_reviews(self):
        client = APIClient()
        user = CustomUser.objects.create(email='testuser@user.fr')
        practitioner = Practitioner.objects.create(
            name="John",
            surname="Doe",
            specialities=["Cardiology"],
            api_id="12345"
        )
        address = Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=10,
            latitude=12.34,
            longitude=56.78
        )
        review = Review.objects.create(
            id_practitioner=practitioner,
            id_user_id=1,
            id_address_id=1,
            review_date="2025-03-17",
            comment="Excellent"
        )
        pathologie = Pathologie.objects.create(
            name="Pathologie1",
            description="Description1"
        )
        Review_Pathologie.objects.create(
            id_review=review,
            id_pathologie=pathologie
        )
        tag = Tag.objects.create(
            type="Professionalism"
        )
        Review_Tag.objects.create(
            id_review=review,
            id_tag=tag,
            rates=1
        )
        url = reverse('practitioner-reviews', args=[practitioner.id])
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['comment'] == review.comment
        assert response.data[0]['review_date'] == str(review.review_date)
        assert len(response.data[0]['pathologies']) == 1
        assert len(response.data[0]['tags']) == 1
