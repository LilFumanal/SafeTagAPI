# Generated by Django 5.0.6 on 2025-03-23 10:07

import SafeTagAPI.models.practitioner_model
import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("line", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=100)),
                ("department", models.BigIntegerField()),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                (
                    "wheelchair_accessibility",
                    models.BooleanField(blank=True, default=None, null=True),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Pathologie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("type", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("username", models.CharField(max_length=30)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True, related_name="custom_user_groups", to="auth.group"
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_user_permissions",
                        to="auth.permission",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("api_organization_id", models.CharField(unique=True)),
                ("name", models.CharField(max_length=255)),
                ("addresses", models.ManyToManyField(to="SafeTagAPI.address")),
            ],
        ),
        migrations.CreateModel(
            name="Practitioner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("surname", models.CharField(max_length=50)),
                (
                    "specialities",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=50),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "accessibilities",
                    models.JSONField(
                        default=SafeTagAPI.models.practitioner_model.default_accessibilities
                    ),
                ),
                (
                    "reimboursement_sector",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("api_id", models.CharField(unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("organizations", models.ManyToManyField(to="SafeTagAPI.organization")),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("review_date", models.DateField()),
                ("comment", models.TextField()),
                (
                    "id_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.address",
                    ),
                ),
                (
                    "id_practitioner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.practitioner",
                    ),
                ),
                (
                    "id_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.customuser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Review_Pathologie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "id_pathologie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.pathologie",
                    ),
                ),
                (
                    "id_review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.review",
                    ),
                ),
            ],
            options={
                "unique_together": {("id_review", "id_pathologie")},
            },
        ),
        migrations.AddField(
            model_name="review",
            name="pathologies",
            field=models.ManyToManyField(
                through="SafeTagAPI.Review_Pathologie", to="SafeTagAPI.pathologie"
            ),
        ),
        migrations.CreateModel(
            name="Review_Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rates",
                    models.IntegerField(choices=[(-1, "Negative"), (1, "Positive")]),
                ),
                (
                    "id_review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.review",
                    ),
                ),
                (
                    "id_tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="SafeTagAPI.tag"
                    ),
                ),
            ],
            options={
                "unique_together": {("id_review", "id_tag")},
            },
        ),
        migrations.AddField(
            model_name="review",
            name="tags",
            field=models.ManyToManyField(
                through="SafeTagAPI.Review_Tag", to="SafeTagAPI.tag"
            ),
        ),
        migrations.CreateModel(
            name="Professional_Tag_Score",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                ("review_count", models.IntegerField(default=0)),
                (
                    "id_practitioner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="SafeTagAPI.practitioner",
                    ),
                ),
                (
                    "id_tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="SafeTagAPI.tag"
                    ),
                ),
            ],
            options={
                "unique_together": {("id_practitioner", "id_tag")},
            },
        ),
    ]
