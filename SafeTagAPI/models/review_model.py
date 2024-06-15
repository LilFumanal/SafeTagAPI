from django.db import models


class Review(models.Model):
    review_date = models.DateField()
    comment = models.TextField()
    id_user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    id_practitioners = models.ForeignKey("Practitioners", on_delete=models.CASCADE)
    pathologies = models.ManyToManyField("Pathologie", through="Review_Pathologie")

    def __str__(self):
        return f"Review by {self.id_user} on {self.id_practitioners}"


class Pathologie(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} , {self.description}"


class Review_Pathologie(models.Model):
    id_review = models.ForeignKey("Review", on_delete=models.CASCADE)
    id_pathologie = models.ForeignKey("Pathologie", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("id_review", "id_pathologie"),)

    def __str__(self):
        return f"Pathologie {self.id_pathologie} in Review {self.id_review}"
