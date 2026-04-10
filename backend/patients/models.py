import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.validators import validate_only_letters, validate_patient_age


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Użytkownik"),
        on_delete=models.PROTECT,
        related_name="patients",
        limit_choices_to={"role": "CLIENT"},
    )
    first_name = models.CharField(
        _("first name"), validators=[validate_only_letters], max_length=64
    )
    last_name = models.CharField(
        _("last name"), validators=[validate_only_letters], max_length=64
    )
    date_of_birth = models.DateField(
        _("Data urodzenia"), validators=[validate_patient_age]
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Pacjent główny"),
        help_text=_("Określa czy pacjent przypisany do klienta określa samego siebie"),
    )

    class Meta:
        db_table = "users_patient"
        verbose_name = _("Pacjent")
        verbose_name_plural = _("Pacjenci")
        ordering = ["-is_primary", "last_name", "first_name"]
        unique_together = ["user", "first_name", "last_name", "date_of_birth"]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
