from django.db import models


class Review(models.Model):
    review_date = models.DateField()
    comment = models.TextField()
    pathologies = models.ManyToManyField("Pathologie", through="Review_Pathologie")
    tags = models.ManyToManyField("Tag", through="Review_Tag")
    id_user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    id_practitioner = models.ForeignKey("Practitioner", on_delete=models.CASCADE)
    id_address = models.ForeignKey("Address", on_delete=models.CASCADE)

    def __str__(self):
        return f"Review by {self.id_user.username} on {self.id_practitioner.name}"


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
