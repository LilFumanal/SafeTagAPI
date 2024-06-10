from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.user_model import User
from ..serializers.user_serializer import UsersSerializer
from ..models.review_model import Review
from ..serializers.review_serializer import ReviewSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def get_queryset(self):
        return User.objects.all()
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        user = self.get_object()
        reviews = Review.objects.filter(id_user=user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
