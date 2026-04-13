import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Therapist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Użytkownik"),
        on_delete=models.CASCADE,
        limit_choices_to={"role": "THERAPIST"},
        related_name="therapist_profile",
        null=True,
        blank=True,
    )
    office = models.OneToOneField(
        "offices.Office",
        on_delete=models.PROTECT,
        related_name="therapist",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "users_therapist"
        verbose_name = _("Terapeuta")
        verbose_name_plural = _("Terapeuci")

    def __str__(self):
        if not self.user:
            return str(_("Nieprzypisany terapeuta"))
        return self.user.get_full_name()


class AvailabilityBlock(models.Model):
    class BlockType(models.TextChoices):
        BASE = "BASE", _("Stały grafik tygodniowy")
        INCLUSION = "INCLUSION", _("Dodatkowa dostępność")
        EXCLUSION = "EXCLUSION", _("Wykluczenie dostępności")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.CASCADE,
        related_name="availability_blocks",
    )
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    type = models.CharField(
        max_length=20,
        choices=BlockType.choices,
        default=BlockType.BASE,
    )

    def clean(self):
        super().clean()

        if self.type == self.BlockType.BASE:
            if self.day_of_week is None:
                raise ValidationError(_("Blok BASE wymaga podania day_of_week"))
            if not 0 <= self.day_of_week <= 6:
                raise ValidationError(_("Nieprawidłowe pole day_of_week"))
            if self.specific_date is not None:
                raise ValidationError(_("Blok BASE nie może zawierać specific_date"))
        else:
            if self.specific_date is None:
                raise ValidationError(
                    _("Blok nadpisania wymaga podania pola specific_date")
                )
            if self.day_of_week is not None:
                raise ValidationError(
                    _("Blok nadpisania nie może zawierać pola day_of_week")
                )

        if self.start_time >= self.end_time:
            raise ValidationError(_("Nieprawidłowy przedział czasu"))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Blok dostępności")
        verbose_name_plural = _("Bloki dostępności")
        ordering = ["day_of_week", "specific_date", "start_time"]
        # Check block rules: either day_of_week or specific_date is set, but not both
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        type="BASE",
                        day_of_week__isnull=False,
                        specific_date__isnull=True,
                    )
                    | Q(
                        type__in=["INCLUSION", "EXCLUSION"],
                        specific_date__isnull=False,
                        day_of_week__isnull=True,
                    )
                ),
                name="availability_block_type_fields_xor",
            )
        ]
        indexes = [
            models.Index(fields=["therapist", "type", "day_of_week"]),
            models.Index(fields=["therapist", "type", "specific_date"]),
        ]
