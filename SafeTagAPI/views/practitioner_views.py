from django.shortcuts import render
from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models.tag_model import Tag
from ..models.practitioner_model import (
    Practitioners,
    Practitioner_Address,
    Organization,
    Professional_Tag_Score,
)
from ..serializers.practitioner_serializer import (
    PractitionerSerializer,
    PractitionerAddressSerializer,
    OrganizationSerializer,
)
from ..serializers.review_serializer import ReviewSerializer
from ..lib.esante_api_treatement import get_practitioner_details, get_all_practitioners, base_url


class PractitionerViewSet(viewsets.ModelViewSet):
    """
    Provides only read operations on Practitioners since their data is managed externally.
    """

    queryset = Practitioners.objects.all()
    serializer_class = PractitionerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "name",
        "surname",
        "specialities",
        "addresses__city",
        "addresses__department",
        "addresses__wheelchair_accesibility",
        "accessibilites"
    ]
    ordering_fields = ["name", "surname", "api_id"]
    
    async def get(self, request, *args, **kwargs):
        page_url = request.query_params.get('page_url', None)
        if not page_url:
            get_all_practitioners(base_url)
        
        practitioners, next_page_url = await get_all_practitioners(page_url)
        return Response({
            'practitioners': practitioners,
            'next_page_url': next_page_url
        }, status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs):
        api_id = request.data.get('api_id')
        if not api_id:
            return Response(
                {"error": "API ID is required to fetch practitioner details."},
                status=status.HTTP_400_BAD_REQUEST
            )
        practitioner_data = get_practitioner_details(api_id)
        if practitioner_data is None:
            return Response(
                {"error": "Failed to fetch practitioner details from the external API."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PractitionerSerializer(data=practitioner_data)
        if serializer.is_valid():
            practitioner = serializer.save()
            return Response(PractitionerSerializer(practitioner).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        practitioner = self.get_object()
        practitioner_data = PractitionerSerializer(practitioner).data
        if practitioner_data:
            tag_averages = practitioner.get_tag_averages()
            response_data = {
                **practitioner_data,  # Include all practitioner fields
                    "tag_summary_list": tag_averages,  # Add tag summary list
            }
            return Response(response_data)
        else:
            return Response(
                {"error": "Practitioner not found"},
                status=status.HTTP_404_NOT_FOUND,
                )

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        practitioner = self.get_object()
        reviews = practitioner.review_set.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def update_accessibilities(self, request):
        """
        Allows users to update accessibility details for practitioners.
        """
        api_id = request.data.get("api_id")
        accessibilities = request.data.get("accessibilities")

        try:
            practitioner = Practitioners.objects.get(api_id=api_id)
        except Practitioners.DoesNotExist:
            return Response(
                {"error": "Practitioner not found"}, status=status.HTTP_404_NOT_FOUND
            )
        practitioner.accessibilities = accessibilities
        practitioner.save()
        return Response(
            PractitionerSerializer(practitioner).data, status=status.HTTP_200_OK
        )


class PractitionerAddressViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Allows updating only the wheelchair accessibility for Practitioner Addresses.
    """

    queryset = Practitioner_Address.objects.all()
    serializer_class = PractitionerAddressSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["line", "city", "department", "wheelchair_accessibility"]

    def update(self, request, *args, **kwargs):
        """
        Restrict updates to only the 'wheelchair_accessibility' field.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data

        if "wheelchair_accessibility" in data:
            instance.wheelchair_accessibility = data["wheelchair_accessibility"]
            instance.save()
            return Response(PractitionerAddressSerializer(instance).data)
        else:
            return Response(
                {"error": "Only wheelchair_accessibility can be updated."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides only read operations on Organizations since their data is managed externally.
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "addresses__city", "addresses__department"]
