from rest_framework import serializers
from ..models.practitioner_model import (
    Practitioner,
    Professional_Tag_Score,
    Address,
    Organization,
)
import logging

logger = logging.getLogger(__name__)

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "line",
            "city",
            "department",
            "latitude",
            "longitude",
            "wheelchair_accessibility",
            "is_active"
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True)

    class Meta:
        model = Organization
        fields = ["api_organization_id", "name", "addresses"]
    
    def get_addresses(self, obj):
        # Filtrer les adresses actives
        addresses = obj.addresses.filter(is_active=True)
        return AddressSerializer(addresses, many=True).data


class PractitionerSerializer(serializers.ModelSerializer):
    organizations = OrganizationSerializer(many=True)

    class Meta:
        model = Practitioner
        fields = [
            "name",
            "surname",
            "specialities",
            "accessibilities",
            "organizations",
            "api_id",  # Add api_id to track the practitioner's source from the API
            "is_active"
        ]

    def create(self, validated_data):
        # Extract nested data for addresses and organizations
        organizations_data = validated_data.pop("organizations", [])

        # Create the practitioner instance with the main validated data
        practitioner = Practitioner.objects.create(**validated_data)

        for organization_data in organizations_data:
            addresses_data = organization_data.pop("addresses", [])
            organization, created = Organization.objects.get_or_create(
                api_organization_id=organization_data.get("api_organization_id"),
                defaults={"name": organization_data.get("name")},
            )
            for address_data in addresses_data:
                address, created = Address.objects.get_or_create(
                    line=address_data["line"],
                    city=address_data["city"],
                    department=address_data["department"],
                    wheelchair_accessibility=address_data["wheelchair_accessibility"],
                    defaults={
                        "latitude": address_data.get("latitude"),
                        "longitude": address_data.get("longitude"),
                        "is_active": True
                    },
                )
                organization.addresses.add(address)
            practitioner.organizations.add(organization)

        return practitioner

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception=raise_exception)
        
        # Vérification de l'api_id
        if self.instance and 'api_id' in self.initial_data and self.initial_data['api_id'] != self.instance.api_id:
            raise serializers.ValidationError({"api_id": "La mise à jour de api_id n'est pas autorisée."})
        return valid
    
    def update(self, instance, validated_data):
        logger.info("Starting update method")
        organizations_data = validated_data.pop("organizations", [])
        logger.info(f"Organizations data: {organizations_data}")

        instance.name = validated_data.get("name", instance.name)
        instance.surname = validated_data.get("surname", instance.surname)
        instance.specialities = validated_data.get("specialities", instance.specialities)
        instance.accessibilities = validated_data.get("accessibilities", instance.accessibilities)
        instance.save()

        if organizations_data:
            instance.organizations.clear()
            for organization_data in organizations_data:
                addresses_data = organization_data.pop("addresses", [])
                logger.info(f"Processing organization: {organization_data}")
                organization, created = Organization.objects.get_or_create(
                    api_organization_id=organization_data.get("api_organization_id"),
                    defaults={"name": organization_data.get("name")},
                )
                if not created:
                    organization.name = organization_data.get("name", organization.name)
                    organization.save()
                for address_data in addresses_data:
                    address, created = Address.objects.get_or_create(
                        line=address_data["line"],
                        city=address_data["city"],
                        department=address_data["department"],
                        wheelchair_accessibility=address_data["wheelchair_accessibility"],
                        defaults={
                            "latitude": address_data.get("latitude"),
                            "longitude": address_data.get("longitude"),
                            "wheelchair_accessibility": address_data.get("wheelchair_accessibility"),
                            "is_active": address_data.get("is_active", True),
                        },
                    )
                    organization.addresses.add(address)
                instance.organizations.add(organization)

        logger.info("Update method completed")

        return instance


class ProfessionalTagScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional_Tag_Score
        fields = ["score", "review_count"]
