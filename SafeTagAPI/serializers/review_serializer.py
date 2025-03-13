from rest_framework import serializers
from ..models.review_model import Pathologie, Review, Review_Pathologie
from ..models.tag_model import Tag, Review_Tag
from ..models.practitioner_model import Practitioner, Address
from .practitioner_serializer import PractitionerSerializer
from ..lib import esante_api_treatement as eat


class PathologieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathologie
        fields = ["name", "description"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "type", "description"]


class ReviewTagSerializer(serializers.ModelSerializer):
    id_tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    rates = serializers.IntegerField()

    class Meta:
        model = Review_Tag
        fields = ["id_tag", "rates"]


class ReviewPathologieSerializer(serializers.ModelSerializer):
    id_pathologie = serializers.PrimaryKeyRelatedField(
        queryset=Pathologie.objects.all()
    )

    class Meta:
        model = Review_Pathologie
        fields = ["id_pathologie"]


class ReviewSerializer(serializers.ModelSerializer):
    tags = ReviewTagSerializer(many=True, source="review_tag_set")
    pathologies = ReviewPathologieSerializer(many=True, source="review_pathologie_set")
    id_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.none()
    )

    class Meta:
        model = Review
        fields = [
            "review_date",
            "comment",
            "id_user",
            "id_practitioner",
            "pathologies",
            "tags",
            "id_address",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        practitioner_id = self.initial_data.get("id_practitioner")
        if practitioner_id:
            self.fields["id_address"].queryset = self.get_addresses_for_practitioner(practitioner_id)

    def get_addresses_for_practitioner(self, practitioner_id):
        try:
            practitioner_instance = Practitioner.objects.get(pk=practitioner_id)
            if not practitioner_instance.organizations.exists():
                raise serializers.ValidationError("The practitioner must be associated with at least one organization.")
            organization_ids = [org.id for org in practitioner_instance.organizations.all()]
            addresses = Address.objects.filter(organization__id__in=organization_ids).distinct()
            if not addresses.exists():
                raise serializers.ValidationError("The organizations must be associated with at least one address.")
            return addresses
        except Practitioner.DoesNotExist:
            raise serializers.ValidationError("The practitioner does not exist.")

    def create(self, validated_data):
        tags_data = validated_data.pop("review_tag_set", [])
        pathologies_data = validated_data.pop("review_pathologie_set", [])
        review = Review.objects.create(**validated_data)

        # Handle tags
        for tag_data in tags_data:
            tag = tag_data["id_tag"]
            rates = tag_data["rates"]
            Review_Tag.objects.create(id_review=review, id_tag=tag, rates=rates)

        # Handle pathologies using the through model
        for pathology_data in pathologies_data:
            pathologie = pathology_data["id_pathologie"]
            Review_Pathologie.objects.create(id_review=review, id_pathologie=pathologie)

        return review
