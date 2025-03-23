import email
from django.test import TestCase
from SafeTagAPI.models.practitioner_model import Organization, Address, Practitioner, Professional_Tag_Score
from SafeTagAPI.models.review_model import Review
from SafeTagAPI.models.tag_model import Review_Tag, Tag
from django.contrib.auth.models import User

from SafeTagAPI.models.user_model import CustomUser

class OrganizationModelTest(TestCase):

    def setUp(self):
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
            line="456 Elm St",
            city="Another City",
            department=2,
            latitude=98.76,
            longitude=54.32,
            wheelchair_accessibility=False,
            is_active=True
        )
        self.organization = Organization.objects.create(
            api_organization_id="123",
            name="Test Organization"
        )
        self.organization.addresses.add(self.address1, self.address2)

    def test_organization_creation(self):
        org = Organization.objects.get(api_organization_id="123")
        self.assertEqual(org.name, "Test Organization")
        self.assertEqual(org.api_organization_id, "123")

    def test_organization_str(self):
        org = Organization.objects.get(api_organization_id="123")
        self.assertEqual(str(org), "Test Organization")

    def test_organization_addresses(self):
        org = Organization.objects.get(api_organization_id="123")
        addresses = org.addresses.all()
        self.assertEqual(addresses.count(), 2)
        self.assertIn(self.address1, addresses)
        self.assertIn(self.address2, addresses)

    def test_add_address_to_organization(self):
        new_address = Address.objects.create(
            line="789 Oak St",
            city="New City",
            department=3,
            latitude=11.11,
            longitude=22.22,
            wheelchair_accessibility=True,
            is_active=True
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

class PractitionerModelTest(TestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            api_organization_id="123",
            name="Test Organization"
        )
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
        self.practitioner = Practitioner.objects.create(
            name="John",
            surname="Doe",
            api_id="1",
            reimboursement_sector="Sector 1"
        )
        self.practitioner.organizations.add(self.organization)
        self.tag1 = Tag.objects.create(type="Discrimination", description="Discrimination Description")
        self.tag2 = Tag.objects.create(type="Homosexualité", description="Homosexualité Description")
        self.user = CustomUser.objects.create(username='testuser',email="test@user.fr")
        self.review1 = Review.objects.create(
            review_date="2023-01-01",
            comment="Positive experience",
            id_user=self.user,
            id_practitioner=self.practitioner,
            id_address=self.address
        )
        self.review2 = Review.objects.create(
            review_date="2023-01-02",
            comment="Negative experience",
            id_user=self.user,
            id_practitioner=self.practitioner,
            id_address=self.address
        )
        Review_Tag.objects.create(id_review=self.review1, id_tag=self.tag1, rates=5)
        Review_Tag.objects.create(id_review=self.review1, id_tag=self.tag2, rates=1)
        Review_Tag.objects.create(id_review=self.review2, id_tag=self.tag2, rates=1)

    def test_practitioner_creation(self):
        practitioner = Practitioner.objects.get(api_id="1")
        self.assertEqual(practitioner.name, "John")
        self.assertEqual(practitioner.surname, "Doe")
        self.assertEqual(practitioner.reimboursement_sector, "Sector 1")

    def test_practitioner_str(self):
        practitioner = Practitioner.objects.get(api_id="1")
        self.assertEqual(str(practitioner), "John Doe")

    def test_practitioner_get_tag_averages(self):
        practitioner = Practitioner.objects.get(api_id="1")
        tag_averages = practitioner.get_tag_averages()
        self.assertEqual(len(tag_averages), 2)
        self.assertEqual(tag_averages[0]['tag'], "Discrimination")
        self.assertEqual(tag_averages[0]['average_rating'], 5)
        self.assertEqual(tag_averages[1]['tag'], "Homosexualité")
        self.assertEqual(tag_averages[1]['average_rating'], 1)

class ProfessionalTagScoreModelTest(TestCase):

    def setUp(self):
        self.practitioner = Practitioner.objects.create(
            name="John",
            surname="Doe",
            api_id="1"
        )
        self.tag = Tag.objects.create(type="Test Type", description="Test Description")
        self.professional_tag_score = Professional_Tag_Score.objects.create(
            id_practitioner=self.practitioner,
            id_tag=self.tag,
            score=10,
            review_count=2
        )

    def test_professional_tag_score_creation(self):
        pts = Professional_Tag_Score.objects.get(id_practitioner=self.practitioner, id_tag=self.tag)
        self.assertEqual(pts.score, 10)
        self.assertEqual(pts.review_count, 2)

    def test_professional_tag_score_str(self):
        pts = Professional_Tag_Score.objects.get(id_practitioner=self.practitioner, id_tag=self.tag)
        self.assertEqual(str(pts), f"Score for {self.practitioner} on Tag {self.tag}")