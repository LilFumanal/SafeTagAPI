from django.core.management.base import BaseCommand
from ...models.tag_model import Tag

class Command(BaseCommand):
    help = "Initialize the fixed set of pathologies in the database"
    initial_tags = [
        "religion",
        "genre",
        "ethnicite",
        "orientation_sexuelle",
        "age",
        "poids",
        "couleur_de_peau",
        "precarite",
        "transidentite",
        "apparence",
        "handicap",
    ]
    def handle(self, *args, **kwargs):
        for tag in self.initial_tags:
            Tag.objects.get_or_create(type=tag, defaults={"description": tag.capitalize()})
        self.stdout.write(self.style.SUCCESS("Successfully initialized tags"))
