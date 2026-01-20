import uuid

from django.core.exceptions import ValidationError
from django.db import models


class AvailabilityBlock(models.Model):
    class AvailabilityBlockType(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly availability slot"
        INCLUSION = "INCLUSION", "Extra availability slot"
        EXCLUSION = "EXCLUSION", "Excluded availability slot"

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
        if self.type == self.BlockType.WEEKLY and self.day_of_week is None:
            raise ValidationError("WEEKLY block requires day_of_week")

        if self.type != self.BlockType.WEEKLY and self.specific_date is None:
            raise ValidationError("Override block requires specific_date")

        if self.start_time >= self.end_time:
            raise ValidationError("Invalid time range")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "availability block"
        verbose_name_plural = "availability blocks"

        indexes = [
            models.Index(fields=["therapist", "day_of_week"]),
            models.Index(fields=["therapist", "specific_date"]),
        ]
