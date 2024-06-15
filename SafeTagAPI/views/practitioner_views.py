from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache

from ..models.practitioner_model import Practitioners, Practitioner_Address, Organization
from ..serializers.practitioner_serializer import PractitionerSerializer, PractitionerAddressSerializer, OrganizationSerializer
from ..serializers.review_serializer import ReviewSerializer
from ..lib.esante_api_treatement import get_practitioner_details  

class PractitionerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides only read operations on Practitioners since their data is managed externally.
    """
    queryset = Practitioners.objects.all()
    serializer_class = PractitionerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'surname', 'specialities', 'addresses__city', 'addresses__department', 'organizations__name']
    ordering_fields = ['name', 'surname', 'api_id']
    
    def retrieve(self, request, *args, **kwargs):
        api_practitioner_id = kwargs['pk']
        cache_key = f"practitioner_{api_practitioner_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        else:
            return get_practitioner_details(api_practitioner_id)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        practitioner = self.get_object()
        reviews = practitioner.review_set.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_accessibilities(self, request):
        """
        Allows users to update accessibility details for practitioners.
        """
        api_id = request.data.get('api_id')
        accessibilities = request.data.get('accessibilities')
        
        try:
            practitioner = Practitioners.objects.get(api_id=api_id)
        except Practitioners.DoesNotExist:
            return Response({'error': 'Practitioner not found'}, status=status.HTTP_404_NOT_FOUND)
        
        practitioner.accessibilities = accessibilities
        practitioner.save()
        return Response(PractitionerSerializer(practitioner).data, status=status.HTTP_200_OK)

class PractitionerAddressViewSet(viewsets.ModelViewSet):
    """
    Allows updating only the wheelchair accessibility for Practitioner Addresses.
    """
    queryset = Practitioner_Address.objects.all()
    serializer_class = PractitionerAddressSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['line', 'city', 'department']

    def update(self, request, *args, **kwargs):
        """
        Restrict updates to only the 'wheelchair_accessibility' field.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data

        if 'wheelchair_accessibility' in data:
            instance.wheelchair_accessibility = data['wheelchair_accessibility']
            instance.save()
            return Response(PractitionerAddressSerializer(instance).data)
        else:
            return Response({'error': 'Only wheelchair_accessibility can be updated.'}, status=status.HTTP_400_BAD_REQUEST)

class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides only read operations on Organizations since their data is managed externally.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'addresses__city', 'addresses__department']
