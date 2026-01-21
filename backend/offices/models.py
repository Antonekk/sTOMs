import uuid

from django.db import models


class Localization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    city = models.CharField(max_length=64)
    postal_code = models.CharField(max_length=16)
    address = models.CharField(max_length=256)

    class Meta:
        verbose_name = "localization"
        verbose_name_plural = "localizations"
        indexes = [
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return self.name


class Office(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    localization = models.ForeignKey(
        Localization, on_delete=models.CASCADE, related_name="offices"
    )
    room_number = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = "office"
        verbose_name_plural = "offices"
        unique_together = ("localization", "room_number")
        indexes = [
            models.Index(fields=["localization"]),
        ]

    def __str__(self):
        return f"{self.localization.name} {self.room_number or ''}"
