from rest_framework import serializers
from ..models.practitioner_model import (
    Practitioner,
    Professional_Tag_Score,
    Practitioner_Address,
    Organization,
)


class PractitionerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practitioner_Address
        fields = [
            "line",
            "city",
            "department",
            "latitude",
            "longitude",
            "wheelchair_accessibility",
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    addresses = PractitionerAddressSerializer(many=True)

    class Meta:
        model = Organization
        fields = ["api_organization_id", "name", "addresses"]


class PractitionerSerializer(serializers.ModelSerializer):
    addresses = PractitionerAddressSerializer(many=True)
    organizations = OrganizationSerializer(many=True)

    class Meta:
        model = Practitioner
        fields = [
            "name",
            "surname",
            "specialities",
            "accessibilities",
            "addresses",
            "organizations",
            "api_id",  # Add api_id to track the practitioner's source from the API
        ]

    def create(self, validated_data):
        # Extract nested data for addresses and organizations
        addresses_data = validated_data.pop("addresses", [])
        organizations_data = validated_data.pop("organizations", [])

        # Create the practitioner instance with the main validated data
        practitioner = Practitioner.objects.create(**validated_data)

        # Process and add addresses to the practitioner
        for address_data in addresses_data:
            address, created = Practitioner_Address.objects.get_or_create(
                line=address_data["line"],
                city=address_data["city"],
                department=address_data["department"],
                defaults={
                    "latitude": address_data.get("latitude"),
                    "longitude": address_data.get("longitude"),
                },
            )
            practitioner.addresses.add(address)

        # Process and add organizations to the practitioner
        for organization_data in organizations_data:
            organization, created = Organization.objects.update_or_create(
                api_organization_id=organization_data.get("api_organization_id"),
                defaults={"name": organization_data.get("name")},
            )
            practitioner.organizations.add(organization)

        return practitioner

    def update(self, instance, validated_data):
        # Extract nested data for addresses and organizations
        addresses_data = validated_data.pop("addresses", [])
        organizations_data = validated_data.pop("organizations", [])

        # Update instance fields
        instance.name = validated_data.get("name", instance.name)
        instance.surname = validated_data.get("surname", instance.surname)
        instance.specialities = validated_data.get(
            "specialities", instance.specialities
        )
        instance.reimboursement_sector = validated_data.get(
            "reimboursement_sector", instance.reimboursement_sector
        )
        instance.save()

        # Clear old addresses and add new ones
        if addresses_data:
            instance.addresses.clear()
            for address_data in addresses_data:
                address, created = Practitioner_Address.objects.get_or_create(
                    line=address_data["line"],
                    city=address_data["city"],
                    department=address_data["department"],
                    defaults={
                        "latitude": address_data.get("latitude"),
                        "longitude": address_data.get("longitude"),
                    },
                )
                instance.addresses.add(address)

        # Clear old organizations and add new ones
        if organizations_data:
            instance.organizations.clear()
            for organization_data in organizations_data:
                org_addresses_data = organization_data.pop("addresses", [])
                organization, created = Organization.objects.update_or_create(
                    api_organization_id=organization_data.get("api_organization_id"),
                    defaults={"name": organization_data.get("name")},
                )
                for org_address_data in org_addresses_data:
                    org_address, created = Practitioner_Address.objects.get_or_create(
                        line=org_address_data["line"],
                        city=org_address_data["city"],
                        department=org_address_data["department"],
                        defaults={
                            "latitude": org_address_data.get("latitude"),
                            "longitude": org_address_data.get("longitude"),
                        },
                    )
                    organization.addresses.add(org_address)
                instance.organizations.add(organization)

        return instance


class ProfessionalTagScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional_Tag_Score
        fields = ["score", "review_count"]
