# Generated by Django 5.0.6 on 2024-06-15 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("SafeTagAPI", "0002_remove_practitioners_accessibility_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="organization",
            name="api_id",
        ),
        migrations.AlterField(
            model_name="practitioners",
            name="api_id",
            field=models.CharField(unique=True),
        ),
    ]
