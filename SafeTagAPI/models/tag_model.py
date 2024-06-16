from django.db import models


class Tag(models.Model):
    type = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return str(self.type)

def load_initial_tags():
    initial_tags = [
        "religion", "genre", "ethnicité", "orientation sexuelle",
        "âge", "poids", "couleur de peau", "précarité",
        "transidentité", "apparence", "handicap"
    ]
    for tag in initial_tags:
        Tag.objects.get_or_create(type=tag, defaults={'description': tag.capitalize()})

class Review_Tag(models.Model):
    id_review = models.ForeignKey("Review", on_delete=models.CASCADE)
    id_tag = models.ForeignKey("Tag", on_delete=models.CASCADE)
    rates = models.IntegerField(choices=[(-1, "Negative"), (1, "Positive")])

    class Meta:
        unique_together = (("id_review", "id_tag"),)

    def __str__(self):
        return f"Tag {self.id_tag} for Review {self.id_review}"
