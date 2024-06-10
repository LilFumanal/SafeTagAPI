from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.practitioner_model import Practitioners, Professional_Tag_Score
from ..models.review_model import Review
from ..serializers.practitioner_serializer import PractitionerSerializer, ProfessionalTagScoreSerializer
from ..serializers.review_serializer import ReviewSerializer

class PractitionersViewSet(viewsets.ModelViewSet):
    queryset = Practitioners.objects.all()
    serializer_class = PractitionerSerializer

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        practitioner = self.get_object()
        reviews = Review.objects.filter(id_practitioners=practitioner)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
class ProfessionalTagScoreViewSet(viewsets.ModelViewSet):
    queryset = Professional_Tag_Score.objects.all()
    serializer_class = ProfessionalTagScoreSerializer