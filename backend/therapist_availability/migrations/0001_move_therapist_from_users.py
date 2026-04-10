import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("offices", "0001_initial"),
        ("users", "0008_alter_patient_first_name_alter_patient_last_name"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Therapist",
                    fields=[
                        (
                            "id",
                            models.UUIDField(
                                default=uuid.uuid4,
                                editable=False,
                                primary_key=True,
                                serialize=False,
                            ),
                        ),
                        (
                            "therapist",
                            models.OneToOneField(
                                blank=True,
                                limit_choices_to={"role": "THERAPIST"},
                                null=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="therapist",
                                to=settings.AUTH_USER_MODEL,
                                verbose_name="Użytkownik",
                            ),
                        ),
                        (
                            "office",
                            models.OneToOneField(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="therapists",
                                to="offices.office",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "users_therapist",
                        "verbose_name": "Terapeuta",
                        "verbose_name_plural": "Terapeuci",
                    },
                ),
            ],
        ),
    ]
