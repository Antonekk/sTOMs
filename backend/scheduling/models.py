import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class AvailabilityBlock(models.Model):
    class AvailabilityBlockType(models.TextChoices):
        WEEKLY = "WEEKLY", _("Blok tygodniowy")
        INCLUSION = "INCLUSION", _("Blok dodatkowych godzin")
        EXCLUSION = "EXCLUSION", _("Blok wyjątkowego braku godzin")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    therapist = models.ForeignKey(
        "users.AppUser",
        on_delete=models.CASCADE,
        related_name="availability_blocks",
    )

    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)
    specific_date = models.DateField(null=True, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    availability_type = models.CharField(
        max_length=20,
        choices=AvailabilityBlockType.choices,
        default=AvailabilityBlockType.WEEKLY,
    )

    def clean(self):
        super().clean()

        # Raise errors in case of invalid usage
        if self.availability_type == self.AvailabilityBlockType.WEEKLY:
            if self.day_of_week is None:
                raise ValidationError(_("Tygodniowy blok wymaga podania day_of_week"))
            if not (0 <= self.day_of_week <= 6):
                raise ValidationError(_("Nieprawidłowe użycie pola day_of_week"))
            if self.specific_date is not None:
                raise ValidationError(
                    _("Blok tygodniowy nie może zawierać specific_date")
                )
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

        indexes = [
            models.Index(fields=["therapist", "day_of_week"]),
            models.Index(fields=["therapist", "specific_date"]),
            models.Index(fields=["therapist", "availability_type"]),
        ]
