from django.forms import ValidationError
import pytest
from rest_framework import serializers
from SafeTagAPI.models.user_model import CustomUser
from SafeTagAPI.serializers.review_serializer import ReviewSerializer
from SafeTagAPI.models.review_model import Review, Pathologie, Review_Pathologie
from SafeTagAPI.models.tag_model import Tag, Review_Tag
from SafeTagAPI.models.practitioner_model import Organization, Practitioner, Address

@pytest.mark.django_db
class TestReviewSerializer:

    def setup_method(self):
        self.user = CustomUser.objects.create(username='testuser')
        self.practitioner = Practitioner.objects.create(name='John', surname='Doe', api_id=1)
        self.organization = Organization.objects.create(name="Test Organization", api_organization_id=1)
        self.address = Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=1,
            latitude=12.34,
            longitude=56.78,
            wheelchair_accessibility=True,
            is_active=True
        )
        self.organization.addresses.add(self.address)
        self.practitioner.organizations.add(self.organization)
        self.pathologie = Pathologie.objects.create(name='Test Pathologie', description='Test Description')
        self.tag = Tag.objects.create(type='Test Type', description='Test Description')

    def test_review_serializer_valid_data(self):
        data = {
            'review_date': '2023-01-01',
            'comment': 'Test Comment',
            'id_user': self.user.id,
            'id_practitioner': self.practitioner.id,
            'pathologies': [{'id_pathologie': self.pathologie.id}],
            'tags': [{'id_tag': self.tag.id, 'rates': 5}],
            'id_address': self.address.id
        }
        serializer = ReviewSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        assert serializer.is_valid()
        review = serializer.save()
        assert review.comment == 'Test Comment'
        assert review.id_user == self.user
        assert review.id_practitioner == self.practitioner
        assert review.id_address == self.address

    def test_review_serializer_invalid_practitioner(self):
        data = {
            'review_date': '2023-01-01',
            'comment': 'Test Comment',
            'id_user': self.user.id,
            'id_practitioner': 999,  # Invalid practitioner ID
            'pathologies': [{'id_pathologie': self.pathologie.id}],
            'tags': [{'id_tag': self.tag.id, 'rates': 5}],
            'id_address': self.address.id
        }
        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer = ReviewSerializer(data=data)
            serializer.is_valid(raise_exception=True)
        assert 'The practitioner does not exist.' in str(excinfo.value)

    def test_review_serializer_invalid_address(self):
        data = {
            'review_date': '2023-01-01',
            'comment': 'Test Comment',
            'id_user': self.user.id,
            'id_practitioner': self.practitioner.id,
            'pathologies': [{'id_pathologie': self.pathologie.id}],
            'tags': [{'id_tag': self.tag.id, 'rates': 5}],
            'id_address': 999  # Invalid address ID
        }
        serializer = ReviewSerializer(data=data)
        assert not serializer.is_valid()
        assert 'id_address' in serializer.errors

    def test_review_serializer_create(self):
        data = {
            'review_date': '2023-01-01',
            'comment': 'Test Comment',
            'id_user': self.user.id,
            'id_practitioner': self.practitioner.id,
            'pathologies': [{'id_pathologie': self.pathologie.id}],
            'tags': [{'id_tag': self.tag.id, 'rates': 5}],
            'id_address': self.address.id
        }
        serializer = ReviewSerializer(data=data)
        assert serializer.is_valid()
        review = serializer.save()
        assert Review.objects.count() == 1
        assert Review_Tag.objects.count() == 1
        assert Review_Pathologie.objects.count() == 1