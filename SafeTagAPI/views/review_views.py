from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.tag_model import Tag, Review_Tag
from ..models.review_model import Review, Review_Pathologie
from ..serializers.review_serializer import ReviewSerializer, ReviewTagSerializer, PathologieSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=True, methods=['get'])
    def tags(self, request, pk=None):
        review = self.get_object()
        review_tags = Review_Tag.objects.filter(id_review=review)
        serializer = ReviewTagSerializer(review_tags, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pathologies(self, request, pk=None):
        review = self.get_object()
        review_pathologies = Review_Pathologie.objects.filter(id_review=review)
        serializer = PathologieSerializer(review_pathologies, many=True)
        return Response(serializer.data)