from django.db import models
from .tag_model import Tag

class Practitioners(models.Model):
    id_practitioner = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    profession = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    accessibility = models.CharField(max_length=100)
    fees = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} {self.surname}"
    
class Professional_Tag_Score(models.Model):
    id_practitioners = models.ForeignKey(Practitioners, on_delete=models.CASCADE)
    id_tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    review_count = models.IntegerField(default=0)

    class Meta:
        unique_together = (('id_practitioners', 'id_tag'),) 
    def __str__(self):
        return f"Score for {self.id_practitioners} on Tag {self.id_tag}"