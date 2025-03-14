# Generated by Django 5.0.6 on 2024-06-16 22:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("SafeTagAPI", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="id_address",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="SafeTagAPI.practitioner_address",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="review",
            name="tags",
            field=models.ManyToManyField(
                through="SafeTagAPI.Review_Tag", to="SafeTagAPI.tag"
            ),
        ),
    ]
