from datetime import date

from django.db import transaction
from django.utils import timezone

from reservations.models import Appointment, AppointmentSeries
from therapist_availability.services.availability import AvailabilityService


class CancellationService:
    @staticmethod
    def _appointment_fits(slots, start_time, end_time) -> bool:
        return any(
            start_time >= slot["start_time"] and end_time <= slot["end_time"]
            for slot in slots
        )

    @classmethod
    @transaction.atomic
    def cancel_conflicting_appointments(cls, therapist, target_date: date | None = None):
        appointments = Appointment.objects.filter(
            appointment_series__therapist=therapist,
            appointment_series__status=AppointmentSeries.Status.ACTIVE,
            status=Appointment.Status.SCHEDULED,
            appointment_date__gte=timezone.localdate(),
        ).select_related("appointment_series")

        if target_date is not None:
            appointments = appointments.filter(appointment_date=target_date)

        canceled = []
        for appointment in appointments:
            series = appointment.appointment_series
            slots = AvailabilityService.get_slots(therapist, appointment.appointment_date)
            if not cls._appointment_fits(
                slots, series.start_time, series.end_time
            ):
                appointment.status = Appointment.Status.CANCELED
                appointment.save(update_fields=["status"])
                canceled.append(appointment)

        if canceled:
            cls._queue_notifications(canceled)

        return canceled

    @staticmethod
    def _queue_notifications(appointments):
        # Celery integration is optional; hook for the notifications module.
        _ = appointments
