import logging
from rest_framework import serializers
from django.test import TestCase
from SafeTagAPI.models.practitioner_model import Practitioner, Address, Organization
from SafeTagAPI.serializers.practitioner_serializer import PractitionerSerializer

logging.basicConfig(level=logging.INFO)

class PractitionerSerializerTest(TestCase):

    def setUp(self):
        self.address_data = {
            "line": "123 Main St",
            "city": "Test City",
            "department": 10,
            "latitude": 12.34,
            "longitude": 56.78,
            "wheelchair_accessibility": True
        }
        self.organization_data = {
            "api_organization_id": 1,
            "name": "Test Organization",
            "addresses": [self.address_data]
        }
        self.practitioner_data = {
            "name": "John",
            "surname": "Doe",
            "specialities": ["Cardiology"],
            "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
            "organizations": [self.organization_data],
            "api_id": 123
        }

    def test_create_practitioner(self):
        serializer = PractitionerSerializer(data=self.practitioner_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        practitioner = serializer.save()
        self.assertEqual(practitioner.name, self.practitioner_data["name"])
        self.assertEqual(practitioner.surname, self.practitioner_data["surname"])
        self.assertEqual(practitioner.specialities, self.practitioner_data["specialities"])
        self.assertEqual(practitioner.accessibilities, self.practitioner_data["accessibilities"])
        self.assertEqual(practitioner.api_id, self.practitioner_data["api_id"])
        self.assertEqual(practitioner.organizations.count(), 1)
        organization = practitioner.organizations.first()
        self.assertEqual(organization.api_organization_id, self.organization_data["api_organization_id"])
        self.assertEqual(organization.name, self.organization_data["name"])
        self.assertEqual(organization.addresses.count(), 1)
        address = organization.addresses.first()
        self.assertEqual(address.line, self.address_data["line"])
        self.assertEqual(address.city, self.address_data["city"])
        self.assertEqual(address.department, self.address_data["department"])
        self.assertEqual(address.latitude, self.address_data["latitude"])
        self.assertEqual(address.longitude, self.address_data["longitude"])

    def test_update_practitioner(self):
        serializer = PractitionerSerializer(data=self.practitioner_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        practitioner = serializer.save()

        updated_data = {
            "name": "Jane",
            "surname": "Smith",
            "specialities": ["Neurology"],
            "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
            "organizations": [{
                "api_organization_id": 2,
                "name": "Updated Organization",
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
            "api_id": 123
        }
        update_serializer = PractitionerSerializer(practitioner, data=updated_data)
        self.assertTrue(update_serializer.is_valid(), update_serializer.errors)
        updated_practitioner = update_serializer.save()
        self.assertEqual(updated_practitioner.name, updated_data["name"])
        self.assertEqual(updated_practitioner.surname, updated_data["surname"])
        self.assertEqual(updated_practitioner.specialities, updated_data["specialities"])
        self.assertEqual(updated_practitioner.accessibilities, updated_data["accessibilities"])
        self.assertEqual(updated_practitioner.api_id, 123)
        self.assertEqual(updated_practitioner.organizations.count(), 1)
        organization = updated_practitioner.organizations.first()
        self.assertEqual(organization.api_organization_id, 2)
        self.assertEqual(organization.name, "Updated Organization")
        self.assertEqual(organization.addresses.count(), 1)
        address = organization.addresses.first()
        self.assertEqual(address.line, self.address_data["line"])
        self.assertEqual(address.city, self.address_data["city"])
        self.assertEqual(address.department, self.address_data["department"])
        self.assertEqual(address.wheelchair_accessibility, self.address_data["wheelchair_accessibility"])
        self.assertEqual(address.latitude, self.address_data["latitude"])
        self.assertEqual(address.longitude, self.address_data["longitude"])

    def test_update_practitioner_with_different_api_id(self):
        serializer = PractitionerSerializer(data=self.practitioner_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        practitioner = serializer.save()

        updated_data = {
            "name": "Jane",
            "surname": "Smith",
            "specialities": ["Neurology"],
            "accessibilities": {"LSF": "Unknown", "Visio": "Unknown"},
            "organizations": [{
                "api_organization_id": 2,
                "name": "Updated Organization",
                "addresses": [{
                    "line": "123 Main St",
                    "city": "Test City",
                    "department": 10,
                    "latitude": 12.34,
                    "longitude": 56.78,
                    "wheelchair_accessibility": True,
                    "is_active":True
                }]
            }],
            "api_id": 456789  # Trying to change api_id
        }
        update_serializer = PractitionerSerializer(practitioner, data=updated_data)
        with self.assertRaises(serializers.ValidationError):
            update_serializer.is_valid(raise_exception=True)

    def test_accessibilities_keys(self):
        serializer = PractitionerSerializer(data=self.practitioner_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        practitioner = serializer.save()
        self.assertIn('LSF', practitioner.accessibilities)
        self.assertIn('Visio', practitioner.accessibilities)