from django.contrib import admin
from SafeTagAPI.models.practitioner_model import (
    Practitioner,
    Professional_Tag_Score,
    Address,
)
from SafeTagAPI.models.review_model import Review
from SafeTagAPI.models.tag_model import Tag, Review_Tag
from SafeTagAPI.models.user_model import CustomUser
from SafeTagAPI.models.review_model import Review_Pathologie, Pathologie


# Register the Practitioner model
@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "surname",
        "specialities",
        "accessibilities",
        "reimboursement_sector",
    )
    search_fields = (
        "name",
        "surname",
        "specialities",
        "reimboursement_sector",
        "accessibilities",
    )
    list_filter = (
        "specialities",
        "reimboursement_sector",
        "accessibilities",
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "line",
        "city",
        "department",
        "latitude",
        "longitude",
        "wheelchair_accessibility",
    )
    search_fields = ("line", "city", "department", "wheelchair_accessibility")
    list_filter = ("city", "department")


# Register the Professional_Tag_Score model
@admin.register(Professional_Tag_Score)
class ProfessionalTagScoreAdmin(admin.ModelAdmin):
    list_display = ("id_practitioner", "id_tag", "score", "review_count")
    list_filter = ("id_practitioner", "id_tag")
    search_fields = (
        "id_practitioner__name",
        "id_practitioner__surname",
        "id_tag__type",
    )


# Register the Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_date", "comment", "id_user", "id_practitioner")
    list_filter = ("review_date", "id_user", "id_practitioner")
    search_fields = (
        "id_practitioner__name",
        "id_practitioner__surname",
    )


# Register the Pathologie model
@admin.register(Pathologie)
class PathologieAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


# Register the Review_Pathologie model
@admin.register(Review_Pathologie)
class ReviewPathologieAdmin(admin.ModelAdmin):
    list_display = ("id_review", "id_pathologie")
    list_filter = ("id_review", "id_pathologie")
    search_fields = ("id_review__comment", "id_pathologie__name")


# Register the Tag model
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("type", "description")
    search_fields = ("type", "description")


# Register the Review_Tag model
@admin.register(Review_Tag)
class ReviewTagAdmin(admin.ModelAdmin):
    list_display = ("id_review", "id_tag", "rates")
    list_filter = ("rates", "id_review", "id_tag")
    search_fields = ("id_review__comment", "id_tag__type")


# Register the CustomUser model
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    list_filter = ("is_staff", "is_superuser")
