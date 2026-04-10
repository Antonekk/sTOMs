from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("patients", "0001_move_patient_from_users"),
        ("reservations", "0003_retarget_patient_therapist_models"),
        ("therapist_availability", "0001_move_therapist_from_users"),
        ("users", "0008_alter_patient_first_name_alter_patient_last_name"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="Patient"),
                migrations.DeleteModel(name="Therapist"),
            ],
        ),
    ]
