from rest_framework import serializers
from ..models.practitioner_model import Practitioners, Professional_Tag_Score

class PractitionerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practitioners
        fields = ['id_practitioner', 'name', 'surname', 'profession', 'city', 'department', 'accessibility', 'fees']

class ProfessionalTagScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional_Tag_Score
        fields = ['score', 'review_count']