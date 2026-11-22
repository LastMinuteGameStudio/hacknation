# Wykaz AED: flaga zasobu i informacje o wykazie zbiorczym (portal/WYKAZ-AED.md)

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0074_auto_20260618_0956"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="is_aed_list",
            field=models.BooleanField(default=False, verbose_name="Wykaz AED"),
        ),
        migrations.CreateModel(
            name="AggregatedAEDInfo",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sources_count", models.PositiveIntegerField(default=0, verbose_name="Dołączone wykazy dostawców")),
                ("skipped_count", models.PositiveIntegerField(default=0, verbose_name="Pominięte wykazy")),
                ("records_count", models.PositiveIntegerField(default=0, verbose_name="Liczba AED")),
                ("duplicates_count", models.PositiveIntegerField(default=0, verbose_name="Oznaczone duplikaty")),
                ("license_name", models.CharField(blank=True, default="", max_length=20, verbose_name="Licencja wykazu")),
                (
                    "report",
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name="Raport scalania"),
                ),
                (
                    "resource",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="resources.Resource",
                        verbose_name="Zasób wykazu zbiorczego",
                    ),
                ),
            ],
            options={
                "verbose_name": "Wykaz zbiorczy AED",
                "verbose_name_plural": "Wykaz zbiorczy AED",
            },
        ),
    ]
