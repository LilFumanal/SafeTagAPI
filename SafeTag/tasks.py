from celery import shared_task
from SafeTagAPI.models.practitioner_model import Practitioner
from SafeTagAPI.lib.esante_api_treatement import get_practitioner_details
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_practitioner_data():
    practitioners = Practitioner.objects.all()
    for practitioner in practitioners:
        try:
            updated_data = get_practitioner_details(practitioner.api_id)
            if updated_data:
                practitioner.name = updated_data.get('name', practitioner.name)
                practitioner.surname = updated_data.get('surname', practitioner.surname)
                practitioner.specialities = updated_data.get('specialities', practitioner.specialities)
                practitioner.organizations = updated_data.get('organizations', practitioner.organizations)
                practitioner.is_active = updated_data.get('is_active', practitioner.is_active)
                practitioner.save()
                logger.info(f"Updated practitioner {practitioner.api_id}")
        except Exception as e:
            logger.error(f"Failed to update practitioner {practitioner.api_id}: {e}")