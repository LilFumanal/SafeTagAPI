from rest_framework import serializers
from SafeTagAPI.models.review_model import Pathologie, Review
from SafeTagAPI.models.tag_model import Tag, Review_Tag
from ..models.practitioner_model import Practitioners
from .practitioner_serializer import PractitionerSerializer
from ..lib import esante_api_treatement as eat


class ReviewSerializer(serializers.ModelSerializer):
    
    def create_review(api_practitioner_id, rating, comment):
    # Check if the practitioner is already in the database
        try:
            practitioner = Practitioners.objects.get(api_id=api_practitioner_id)
        except Practitioners.DoesNotExist:
            # Fetch practitioner details from the API
            practitioner_details = eat.get_practitionner_details(api_practitioner_id)
            if not practitioner_details:
                print("Unable to fetch practitioner details from the API.")
                return None
            
            # Serialize and create the practitioner
            serializer = PractitionerSerializer(data=practitioner_details)
            if serializer.is_valid():
                practitioner = serializer.save()
            else:
                print("Validation error:", serializer.errors)
                return None

        # Create the review
        review = Review.objects.create(
            practitioner=practitioner,
            rating=rating,
            comment=comment
        )
        return review
    class Meta:
        model = Review
        fields = ["review_date", "comment"]


class PathologieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathologie
        fields = ["name", "description"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["type", "description"]


class ReviewTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review_Tag
        fields = "rating"
