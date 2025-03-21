import os
from socket import timeout
from asgiref.sync import sync_to_async
from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views import View
from django.http import JsonResponse
from aiocache import Cache
from aiocache.serializers import JsonSerializer
import psutil
import json
from ..lib.logger import Logger
from ..models.review_model import Review
from ..models.practitioner_model import (
    Practitioner,
    Address,
    Organization)
from ..serializers.practitioner_serializer import (
    PractitionerSerializer,
    AddressSerializer,
    OrganizationSerializer,
)
from ..serializers.review_serializer import ReviewSerializer
from ..lib.esante_api_treatement import get_practitioner_details, get_all_practitioners

    
cache = Cache(
    Cache.REDIS, 
    endpoint="localhost",  # Modifier selon ta config Redis
    port=6379,  
    serializer=JsonSerializer(), 
    timeout=24 * 60 * 60  # Cache 24h
)
logger = Logger(__name__).get_logger()

def log_open_files():
    process = psutil.Process(os.getpid())
    open_files = process.open_files()
    print(f"Open files: {len(open_files)}")
    open_connections = process.net_connections()
    print(f"Open connections: {len(open_connections)}")
    
class PractitionerAsyncViews(View):
    async def get(self, request, *args, **kwargs):
        try:
            page_url = request.GET.get('page_url', '', timeout=5)
            log_open_files()
            practitioners, next_page_url = await get_all_practitioners()
            response_data = {
                'practitioners': practitioners,
                'next_page_url': next_page_url
            }
            return JsonResponse(response_data, status=200)
        except Exception as e:
            logger.error(f"Error during async operation: {e}")
            return JsonResponse({'error': e}, status=500)
        
    async def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            api_id = body.get('api_id')
            if not api_id:
                return JsonResponse(
                    {"error": "API ID is required to fetch practitioner details."},
                    status=400
                )
            practitioner_data = await get_practitioner_details(api_id)
            if practitioner_data is None:
                return JsonResponse(
                    {"error": "Failed to fetch practitioner details from the external API."},
                    status=400
                )
            serializer = PractitionerSerializer(data=practitioner_data)
            if serializer.is_valid():
                practitioner = serializer.save()
                return JsonResponse(PractitionerSerializer(practitioner).data, status=201)
            else:
                return JsonResponse(serializer.errors, status=400)
        except Exception as e:
            return JsonResponse({'error': e}, status=500)

class PractitionerViewSet(viewsets.ViewSet):
    """
    Provides only read operations on Practitioner since their data is managed externally.
    """
    queryset = Practitioner.objects.all()
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

    def retrieve(self, request, *args, **kwargs):
        from django.shortcuts import get_object_or_404
        practitioner = get_object_or_404(Practitioner, pk=kwargs['pk'])
        practitioner_data = PractitionerSerializer(practitioner).data
        if practitioner_data:
            tag_averages = practitioner.get_tag_averages()
            response_data = {
                **practitioner_data,  # Include all practitioner fields
                    "tag_summary_list": tag_averages,  # Add tag summary list
            }
            return Response(response_data)

    @action(detail=True, methods=["get"], url_path='reviews', url_name='reviews')
    def reviews(self, request, *args, **kwargs):
        reviews = Review.objects.filter(id_practitioner_id=kwargs['pk']).prefetch_related('review_tag_set')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path='update-accessibilities', url_name='update-accessibilities')
    async def update_accessibilities(self, request):
        """
        Allows users to update accessibility details for practitioner.
        """
        api_id = request.data.get("api_id")
        accessibilities = request.data.get("accessibilities")

        try:
            practitioner = await Practitioner.objects.aget(api_id=api_id)
        except Practitioner.DoesNotExist:
            return Response(
                {"error": "Practitioner not found"}, status=status.HTTP_404_NOT_FOUND
            )
        practitioner.accessibilities = accessibilities
        await sync_to_async(practitioner.save)()
        return Response(
            PractitionerSerializer(practitioner).data, status=status.HTTP_200_OK
        )


class AddressViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Allows updating only the wheelchair accessibility for Practitioner Addresses.
    """

    queryset = Address.objects.all()
    serializer_class = AddressSerializer
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
            return Response(AddressSerializer(instance).data)
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
