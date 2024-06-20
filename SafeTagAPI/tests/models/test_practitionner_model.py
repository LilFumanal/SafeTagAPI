# SafeTagAPI/tests.py

from django.test import TestCase
from SafeTagAPI.models.tag_model import Tag
from SafeTagAPI.models import Practitioner_Address, Organization, Practitioners, Professional_Tag_Score
from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum

class PractitionerAddressModelTest(TestCase):
    def test_practitioner_address_creation(self):
        address = Practitioner_Address.objects.create(
            line="123 Health St",
            city="Healthville",
            department=101,
            latitude=45.123,
            longitude=-93.456,
            wheelchair_accessibility=True
        )
        self.assertEqual(str(address), "123 Health St, Healthville")
        self.assertEqual(address.city, "Healthville")
        self.assertTrue(address.wheelchair_accessibility)

class OrganizationModelTest(TestCase):
    def test_organization_creation(self):
        address = Practitioner_Address.objects.create(
            line="123 Health St",
            city="Healthville",
            department=101
        )
        organization = Organization.objects.create(
            api_organization_id="org123",
            name="Health Organization"
        )
        organization.addresses.add(address)
        
        self.assertEqual(str(organization), "Health Organization")
        self.assertEqual(organization.addresses.count(), 1)
        self.assertIn(address, organization.addresses.all())

class PractitionersModelTest(TestCase):
    def setUp(self):
        self.address = Practitioner_Address.objects.create(
            line="456 Wellness Ave",
            city="Wellnessville",
            department=102
        )
        self.organization = Organization.objects.create(
            api_organization_id="org456",
            name="Wellness Organization"
        )
        self.practitioner = Practitioners.objects.create(
            name="John",
            surname="Doe",
            reimboursement_sector="Sector A",
            api_id="pract123"
        )
        self.practitioner.addresses.add(self.address)
        self.practitioner.organizations.add(self.organization)

    def test_practitioner_creation(self):
        self.assertEqual(str(self.practitioner), "John Doe")
        self.assertIn(self.address, self.practitioner.addresses.all())
        self.assertIn(self.organization, self.practitioner.organizations.all())

    def test_get_tag_summary(self):
        tag = Tag.objects.create(type="General")
        tag_score = Professional_Tag_Score.objects.create(
            id_practitioners=self.practitioner,
            id_tag=tag,
            score=4,
            review_count=10
        )
        
        summary = self.practitioner.get_tag_summary()
        
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]['average_rating'], 4)
        self.assertEqual(summary[0]['total_reviews'], 10)

class ProfessionalTagScoreModelTest(TestCase):
    def setUp(self):
        self.practitioner = Practitioners.objects.create(
            name="Jane",
            surname="Smith",
            reimboursement_sector="Sector B",
            api_id="pract456"
        )
        self.tag = Tag.objects.create(type="Special")

    def test_professional_tag_score_creation(self):
        tag_score = Professional_Tag_Score.objects.create(
            id_practitioners=self.practitioner,
            id_tag=self.tag,
            score=5,
            review_count=20
        )
        
        self.assertEqual(str(tag_score), f"Score for {self.practitioner} on Tag {self.tag}")
        self.assertEqual(tag_score.score, 5)
        self.assertEqual(tag_score.review_count, 20)
