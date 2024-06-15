from django.core.management.base import BaseCommand
from ...models.review_model import Pathologie
from ...lib.pathologies_dictionary import DSM5Pathologies


class Command(BaseCommand):
    help = "Initialize the fixed set of pathologies in the database"

    def handle(self, *args, **kwargs):
        for name, description in DSM5Pathologies.items():
            Pathologie.objects.get_or_create(name=name, description=description)
        self.stdout.write(self.style.SUCCESS("Successfully initialized pathologies"))
