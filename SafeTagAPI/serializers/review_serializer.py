from rest_framework import serializers
from ..models.review_model import Pathologie, Review
from ..models.tag_model import Tag, Review_Tag

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id_reviews', 'review_date', 'comment']

class PathologieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathologie
        fields = ['name', 'description']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['type', 'description']

class ReviewTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review_Tag
        fields = 'rating'