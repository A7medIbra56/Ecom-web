# Generated by Django 5.1.5 on 2025-02-28 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendor", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
