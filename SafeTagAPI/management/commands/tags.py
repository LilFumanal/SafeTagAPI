from django.core.management.base import BaseCommand
from ...models.tag_model import Tag

def load_initial_tags():
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
    for tag in initial_tags:
        Tag.objects.get_or_create(type=tag, defaults={"description": tag.capitalize()})

