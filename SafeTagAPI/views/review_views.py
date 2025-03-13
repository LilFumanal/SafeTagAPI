from datetime import date
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models.review_model import Review, Pathologie
from ..models.tag_model import Review_Tag
from ..models.practitioner_model import Practitioner
from ..serializers.review_serializer import (
    ReviewSerializer,
    PathologieSerializer,
    ReviewTagSerializer,
)
from ..serializers.practitioner_serializer import (
    Address,
    PractitionerSerializer,
)
from ..lib.esante_api_treatement import get_practitioner_details


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for reviews.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle fetching practitioner data from the API if not present.
        """
        api_practitioner_id = request.data.get("id_practitioner")
        tags = request.data.get("tags", [])
        pathologies = request.data.get("pathologies", [])
        address_id = request.data.get("id_address")
        comment = request.data.get("comment")
        review_date = date.today()

        # Fetch practitioner data if it doesn't exist
        practitioner = Practitioner.objects.filter(api_id=api_practitioner_id).first()
        if not practitioner:
            practitioner_data = get_practitioner_details(api_practitioner_id)
            if practitioner_data:
                practitioner_serializer = PractitionerSerializer(data=practitioner_data)
                if practitioner_serializer.is_valid():
                    practitioner = practitioner_serializer.save()
                else:
                    return Response(
                        practitioner_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": "Practitioner data could not be fetched from the API."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Create the review
        review_data = {
            "id_practitioner": practitioner.id,
            "review_date": review_date,
            "comment": comment,
            "tags": tags,
            "pathologies": pathologies,
            "id_address": address_id,
            "id_user": 1,  # Assuming user is authenticated and using `request.user`
            # 'id_user': request.user.id  # Assuming user is authenticated and using `request.user`
        }
        review_serializer = ReviewSerializer(data=review_data)
        if review_serializer.is_valid():
            review_serializer.save()
            return Response(review_serializer.data, status=status.HTTP_201_CREATED)
        return Response(review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def practitioner_reviews(self, request, pk=None):
        reviews = Review.objects.filter(id_practitioner_id=pk)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
