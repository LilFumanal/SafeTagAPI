from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db.models import PointField

from SafeTagAPI.models import tag_model


class Practitioner_Address(models.Model):
    line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    department = models.BigIntegerField()
    location = PointField(geography=True, null=True, blank=True)
    wheelchair_accessibility = models.BooleanField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.line}, {self.city}"


class Organization(models.Model):
    api_organization_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    addresses = models.ManyToManyField(Practitioner_Address, blank=True)

    def __str__(self):
        return f"{self.name}"


def default_accessibilities():
    return {"LSF": "Unknown", "Visio": "Unknown"}


class Practitioner(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    specialities = ArrayField(
        models.CharField(max_length=50),  # Type des éléments dans l'ArrayField
        blank=True,
        default=list,
    )
    accessibilities = models.JSONField(
        default=default_accessibilities,
    )
    reimboursement_sector = models.CharField(max_length=100)
    organizations = models.ManyToManyField(Organization, blank=True)
    addresses = models.ManyToManyField(Practitioner_Address)
    api_id = models.CharField(unique=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_tag_averages(self):
        # Direct aggregation and formatting in one step
        return (
            tag_model.Review_Tag.objects
            .filter(id_review__id_practitioners=self)
            .values(tag_type=models.F("id_tag__type"))  # Use F expression for clarity
            .annotate(average_rating=models.Avg("rates"))  # Aggregate average rating
            .order_by("tag_type")  # Optional, but ensures consistent ordering
        )


class Professional_Tag_Score(models.Model):
    practitioner: models.ForeignKey = models.ForeignKey(
        "Practitioner", on_delete=models.CASCADE
    )
    id_tag = models.ForeignKey("Tag", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)

    class Meta:
        unique_together = (("practitioner", "id_tag"),)

    def __str__(self):
        return f"Score for {self.practitioner} on Tag {self.id_tag}"
