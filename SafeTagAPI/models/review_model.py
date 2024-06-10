from django.db import models

from ..models.practitioner_model import Practitioners
from ..models.user_model import User

class Review(models.Model):
    id_reviews = models.AutoField(primary_key=True)
    review_date = models.DateField()
    comment = models.TextField()
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_practitioners = models.ForeignKey(Practitioners, on_delete=models.CASCADE)

    def __str__(self):
        return f"Review by {self.id_user} on {self.id_practitioners}"
    
class Pathologie(models.Model):
    id_pathologie = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)
    
class Review_Pathologie(models.Model):
    id_review = models.ForeignKey(Review, on_delete=models.CASCADE)
    id_pathologie = models.ForeignKey(Pathologie, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('id_review', 'id_pathologie'),)

    def __str__(self):
        return f"Pathologie {self.id_pathologie} in Review {self.id_review}"