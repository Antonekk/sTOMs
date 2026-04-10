import uuid

import django.db.models.deletion
import users.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0008_alter_patient_first_name_alter_patient_last_name"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Patient",
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
                            "first_name",
                            models.CharField(
                                max_length=64,
                                validators=[users.validators.validate_only_letters],
                                verbose_name="first name",
                            ),
                        ),
                        (
                            "last_name",
                            models.CharField(
                                max_length=64,
                                validators=[users.validators.validate_only_letters],
                                verbose_name="last name",
                            ),
                        ),
                        (
                            "date_of_birth",
                            models.DateField(
                                validators=[users.validators.validate_patient_age],
                                verbose_name="Data urodzenia",
                            ),
                        ),
                        (
                            "is_primary",
                            models.BooleanField(
                                default=False,
                                help_text="Określa czy pacjent przypisany do klienta określa samego siebie",
                                verbose_name="Pacjent główny",
                            ),
                        ),
                        (
                            "user",
                            models.ForeignKey(
                                limit_choices_to={"role": "CLIENT"},
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="patients",
                                to=settings.AUTH_USER_MODEL,
                                verbose_name="Użytkownik",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "users_patient",
                        "verbose_name": "Pacjent",
                        "verbose_name_plural": "Pacjenci",
                        "ordering": ["-is_primary", "last_name", "first_name"],
                        "unique_together": {
                            ("user", "first_name", "last_name", "date_of_birth")
                        },
                    },
                ),
            ],
        ),
    ]
