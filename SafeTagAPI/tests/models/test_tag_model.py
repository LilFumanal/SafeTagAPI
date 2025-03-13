from django.test import TestCase
from SafeTagAPI.models.tag_model import Tag, Review_Tag
from SafeTagAPI.models.review_model import Review
from SafeTagAPI.models import CustomUser, Practitioner, Address

class ReviewTagModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser", password="password")
        self.practitioner = Practitioner.objects.create(name="John", surname="Doe",api_id=1)
        self.address = Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=1,
            latitude=12.34,
            longitude=56.78,
            wheelchair_accessibility=True
        )
        self.review = Review.objects.create(
            review_date="2023-01-01",
            comment="Test Comment",
            id_user=self.user,
            id_practitioner=self.practitioner,
            id_address=self.address
        )
        self.tag = Tag.objects.create(type="Positive", description="Positive feedback")
        self.review_tag = Review_Tag.objects.create(id_review=self.review, id_tag=self.tag, rates=1)

    def test_review_tag_creation(self):
        review_tag = Review_Tag.objects.get(id=self.review_tag.id)
        self.assertEqual(review_tag.id_review, self.review)
        self.assertEqual(review_tag.id_tag, self.tag)
        self.assertEqual(review_tag.rates, 1)

    def test_review_tag_str(self):
        review_tag = Review_Tag.objects.get(id=self.review_tag.id)
        self.assertEqual(str(review_tag), f"Tag {self.tag} for Review {self.review}")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Review_Tag.objects.create(id_review=self.review, id_tag=self.tag, rates=1)

    def test_tag_creation(self):
        tag = Tag.objects.get(id=self.tag.id)
        self.assertEqual(tag.type, "Positive")
        self.assertEqual(tag.description, "Positive feedback")

    def test_tag_str(self):
        tag = Tag.objects.get(id=self.tag.id)
        self.assertEqual(str(tag), "Positive")