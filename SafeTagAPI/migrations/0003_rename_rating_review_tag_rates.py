# Generated by Django 5.0.6 on 2024-06-16 22:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("SafeTagAPI", "0002_review_id_address_review_tags"),
    ]

    operations = [
        migrations.RenameField(
            model_name="review_tag",
            old_name="rating",
            new_name="rates",
        ),
    ]
