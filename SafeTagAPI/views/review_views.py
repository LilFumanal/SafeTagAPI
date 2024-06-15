from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..models.review_model import Review, Pathologie
from ..models.tag_model import Review_Tag
from ..models.practitioner_model import Practitioners
from ..serializers.review_serializer import ReviewSerializer, PathologieSerializer, ReviewTagSerializer
from ..serializers.practitioner_serializer import Practitioner_Address, PractitionerSerializer
from ..lib.esante_api_treatement import get_practitioner_details

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle fetching practitioner data from the API if not present.
        """
        api_practitioner_id = request.data.get('api_practitioner_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        
        # Fetch practitioner data if it doesn't exist
        practitioner = Practitioners.objects.filter(api_id=api_practitioner_id).first()
        if not practitioner:
            practitioner_data = get_practitioner_details(api_practitioner_id)
            if practitioner_data:
                practitioner_serializer = PractitionerSerializer(data=practitioner_data)
                if practitioner_serializer.is_valid():
                    practitioner = practitioner_serializer.save()
                else:
                    return Response(practitioner_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Practitioner data could not be fetched from the API.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create the review
        review_data = {
            'id_practitioners': practitioner.id,
            'comment': comment,
            'rating': rating,
            'id_user': request.user.id
        }
        review_serializer = ReviewSerializer(data=review_data)
        if review_serializer.is_valid():
            review_serializer.save()
            return Response(review_serializer.data, status=status.HTTP_201_CREATED)
        return Response(review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PathologieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides read operations for DSM-5 pathologies.
    """
    queryset = Pathologie.objects.all()
    serializer_class = PathologieSerializer

class TagViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for tags.
    """
    queryset = Review_Tag.objects.all()
    serializer_class = ReviewTagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
