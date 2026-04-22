import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from patients.models import Patient
from therapist_availability.models import Therapist


class AppointmentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    duration_time_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_periodic = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Rodzaj wizyty")
        verbose_name_plural = _("Rodzaje wizyt")

    def __str__(self):
        return self.name


class AppointmentSeries(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Aktywna")
        ENDED = "ENDED", _("Zakończona")
        CANCELED = "CANCELED", _("Anulowana")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    therapist = models.ForeignKey(
        Therapist, on_delete=models.PROTECT, related_name="appointment_series"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="appointment_series"
    )
    appointment_type = models.ForeignKey(
        AppointmentType, on_delete=models.PROTECT, related_name="appointment_series"
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField()
    is_weekly = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    creation_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "appointment series"
        verbose_name_plural = "appointment series"

    @property
    def is_recurring(self) -> bool:
        return self.is_weekly


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", _("Zaplanowana")
        COMPLETED = "COMPLETED", _("Zakończona")
        CANCELED = "CANCELED", _("Anulowana")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    appointment_series = models.ForeignKey(
        AppointmentSeries, on_delete=models.CASCADE, related_name="appointments"
    )
    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
    )

    appointment_date = models.DateField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )

    final_price = models.DecimalField(max_digits=5, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.appointment_series_id:
            series = self.appointment_series
            if self.therapist_id is None:
                self.therapist_id = series.therapist_id
            if self.patient_id is None:
                self.patient_id = series.patient_id
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(
                fields=["therapist", "appointment_date", "status"],
                name="appt_therapist_date_status_idx",
            ),
            models.Index(
                fields=["patient", "appointment_date"],
                name="appt_patient_date_idx",
            ),
        ]
