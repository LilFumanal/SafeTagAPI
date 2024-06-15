from django.db import models
from django.contrib.postgres.fields import ArrayField

    
class Practitioner_Address(models.Model):
    line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    department = models.BigIntegerField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    wheelchair_accessibility = models.BooleanField(blank = True, default = None)

    def __str__(self):
        return f"{self.line}, {self.city}, {self.postal_code}"

class Organization(models.Model):
    name = models.CharField(max_length=255)
    api_id= models.BigIntegerField()
    addresses = models.ManyToManyField(Practitioner_Address, blank=True)

    def __str__(self):
        return self.name
    
def default_accessibilities():
    return {"LSF": "Unknown", "Visio": "Unknown"}
class Practitioners(models.Model):
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
    api_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return f"{self.name} {self.surname}"


class Professional_Tag_Score(models.Model):
    id_practitioners: models.ForeignKey = models.ForeignKey(
        "Practitioners", on_delete=models.CASCADE
    )
    id_tag= models.ForeignKey("Tag", on_delete=models.CASCADE)
    score= models.IntegerField(default=0)
    review_count= models.IntegerField(default=0)

    class Meta:
        unique_together = (("id_practitioners", "id_tag"),)

    def __str__(self):
        return f"Score for {self.id_practitioners} on Tag {self.id_tag}"
