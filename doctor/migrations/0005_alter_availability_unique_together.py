# Generated by Django 4.2.4 on 2023-10-20 10:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0004_remove_appointments_date_remove_appointments_time_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="availability",
            unique_together={("doctor", "date", "time_slot")},
        ),
    ]
