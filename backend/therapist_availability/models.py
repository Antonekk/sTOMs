import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Therapist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    therapist = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Użytkownik"),
        on_delete=models.CASCADE,
        limit_choices_to={"role": "THERAPIST"},
        related_name="therapist",
        # TODO: Remove after therapist profile creation is mandatory.
        null=True,
        blank=True,
    )
    office = models.OneToOneField(
        "offices.Office",
        on_delete=models.PROTECT,
        related_name="therapists",
        # TODO: Remove after office assignment is mandatory.
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "users_therapist"
        verbose_name = _("Terapeuta")
        verbose_name_plural = _("Terapeuci")

    def __str__(self):
        if not self.therapist:
            return str(_("Nieprzypisany terapeuta"))
        return self.therapist.get_full_name()
