from django.test import TestCase
from SafeTagAPI.models.practitioner_model import Organization, Practitioner_Address

# SafeTagAPI/models/test_practitioner_model.py


class OrganizationModelTest(TestCase):

    def setUp(self):
        self.address1 = Practitioner_Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=1,
            latitude=12.34,
            longitude=56.78,
            wheelchair_accessibility=True
        )
        self.address2 = Practitioner_Address.objects.create(
            line="456 Elm St",
            city="Another City",
            department=2,
            latitude=98.76,
            longitude=54.32,
            wheelchair_accessibility=False
        )
        self.organization = Organization.objects.create(
            api_organization_id="org123",
            name="Test Organization"
        )
        self.organization.addresses.add(self.address1, self.address2)

    def test_organization_creation(self):
        org = Organization.objects.get(api_organization_id="org123")
        self.assertEqual(org.name, "Test Organization")
        self.assertEqual(org.api_organization_id, "org123")

    def test_organization_str(self):
        org = Organization.objects.get(api_organization_id="org123")
        self.assertEqual(str(org), "Test Organization")

    def test_organization_addresses(self):
        org = Organization.objects.get(api_organization_id="org123")
        addresses = org.addresses.all()
        self.assertEqual(addresses.count(), 2)
        self.assertIn(self.address1, addresses)
        self.assertIn(self.address2, addresses)

    def test_add_address_to_organization(self):
        new_address = Practitioner_Address.objects.create(
            line="789 Oak St",
            city="New City",
            department=3,
            latitude=11.11,
            longitude=22.22,
            wheelchair_accessibility=True
        )
        self.organization.addresses.add(new_address)
        addresses = self.organization.addresses.all()
        self.assertEqual(addresses.count(), 3)
        self.assertIn(new_address, addresses)

    def test_remove_address_from_organization(self):
        self.organization.addresses.remove(self.address1)
        addresses = self.organization.addresses.all()
        self.assertEqual(addresses.count(), 1)
        self.assertNotIn(self.address1, addresses)
        self.assertIn(self.address2, addresses)

if __name__ == '__main__':
    unittest.main()