import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("patients", "0001_move_patient_from_users"),
        ("reservations", "0002_alter_appointmenttype_options_and_more"),
        ("therapist_availability", "0001_move_therapist_from_users"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="appointmentseries",
                    name="patient",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="appointment_series",
                        to="patients.patient",
                    ),
                ),
                migrations.AlterField(
                    model_name="appointmentseries",
                    name="therapist",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="appointment_series",
                        to="therapist_availability.therapist",
                    ),
                ),
            ],
        ),
    ]
