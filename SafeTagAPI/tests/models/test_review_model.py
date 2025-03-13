from django.test import TestCase
from SafeTagAPI.models.user_model import CustomUser
from SafeTagAPI.models.practitioner_model import Practitioner, Address
from SafeTagAPI.models.review_model import Review, Pathologie, Review_Pathologie
from SafeTagAPI.models.tag_model import Review_Tag, Tag

class ReviewModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser", password="password")
        self.practitioner = Practitioner.objects.create(name="John", surname="Doe", api_id=1)
        self.address = Address.objects.create(
            line="123 Main St",
            city="Test City",
            department=1,
            latitude=12.34,
            longitude=56.78,
            wheelchair_accessibility=True,
            is_active=True
        )
        self.pathologie = Pathologie.objects.create(name="Test Pathologie", description="Test Description")
        self.tag = Tag.objects.create(type="TestTag")
        self.review = Review.objects.create(
            review_date="2023-01-01",
            comment="Test Comment",
            id_user=self.user,
            id_practitioner=self.practitioner,
            id_address=self.address
        )
        Review_Pathologie.objects.create(id_review=self.review, id_pathologie=self.pathologie)
        Review_Tag.objects.create(id_review=self.review, id_tag=self.tag, rates=1)

    def test_review_creation(self):
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(review.comment, "Test Comment")
        self.assertEqual(review.id_user, self.user)
        self.assertEqual(review.id_practitioner, self.practitioner)
        self.assertEqual(review.id_address, self.address)

    def test_review_str(self):
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(str(review), f"Review by {self.user.username} on {self.practitioner.name}")

    def test_pathologie_creation(self):
        pathologie = Pathologie.objects.get(id=self.pathologie.id)
        self.assertEqual(pathologie.name, "Test Pathologie")
        self.assertEqual(pathologie.description, "Test Description")

    def test_pathologie_str(self):
        pathologie = Pathologie.objects.get(id=self.pathologie.id)
        self.assertEqual(str(pathologie), "Test Pathologie , Test Description")

    def test_review_pathologie_creation(self):
        review_pathologie = Review_Pathologie.objects.get(id_review=self.review, id_pathologie=self.pathologie)
        self.assertEqual(review_pathologie.id_review, self.review)
        self.assertEqual(review_pathologie.id_pathologie, self.pathologie)

    def test_review_pathologie_str(self):
        review_pathologie = Review_Pathologie.objects.get(id_review=self.review, id_pathologie=self.pathologie)
        self.assertEqual(str(review_pathologie), f"Pathologie {self.pathologie} in Review {self.review}")