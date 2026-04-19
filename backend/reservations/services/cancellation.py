from datetime import date, datetime, timedelta

from constance import config
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException

from reservations.models import Appointment, AppointmentSeries
from therapist_availability.services.availability import AvailabilityService


class CancellationWindowError(APIException):
    status_code = 409
    default_detail = "Anulowanie wizyty nie jest możliwe w wyznaczonym oknie czasowym."
    default_code = "cancellation_window"


class CancellationService:
    @staticmethod
    def _appointment_start_datetime(appointment: Appointment) -> datetime:
        series = appointment.appointment_series
        return timezone.make_aware(
            datetime.combine(appointment.appointment_date, series.start_time)
        )

    @classmethod
    def _within_cancellation_window(cls, appointment: Appointment) -> bool:
        window = timedelta(hours=config.CANCELLATION_WINDOW_HOURS)
        return cls._appointment_start_datetime(appointment) - timezone.now() >= window

    @classmethod
    def _queue_notifications(cls, appointments):
        _ = appointments

    @classmethod
    @transaction.atomic
    def cancel_appointment(cls, appointment: Appointment, *, enforce_window: bool = True):
        if appointment.status != Appointment.Status.SCHEDULED:
            return appointment

        if enforce_window and not cls._within_cancellation_window(appointment):
            raise CancellationWindowError()

        appointment.status = Appointment.Status.CANCELED
        appointment.save(update_fields=["status"])
        cls._update_series_after_appointment_change(appointment.appointment_series)
        cls._queue_notifications([appointment])
        return appointment

    @classmethod
    @transaction.atomic
    def cancel_series(cls, series: AppointmentSeries):
        if series.status == AppointmentSeries.Status.CANCELED:
            return series

        today = timezone.localdate()
        future_appointments = series.appointments.filter(
            status=Appointment.Status.SCHEDULED,
            appointment_date__gte=today,
        )
        canceled = list(future_appointments)
        future_appointments.update(status=Appointment.Status.CANCELED)

        series.status = AppointmentSeries.Status.CANCELED
        series.save(update_fields=["status"])

        if canceled:
            cls._queue_notifications(canceled)
        return series

    @classmethod
    def _appointment_fits(cls, slots, start_time, end_time) -> bool:
        return any(
            start_time >= slot["start_time"] and end_time <= slot["end_time"]
            for slot in slots
        )

    @classmethod
    @transaction.atomic
    def cancel_conflicting_appointments(cls, therapist, target_date: date | None = None):
        appointments = Appointment.objects.filter(
            therapist=therapist,
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
            if not cls._appointment_fits(slots, series.start_time, series.end_time):
                appointment.status = Appointment.Status.CANCELED
                appointment.save(update_fields=["status"])
                canceled.append(appointment)
                cls._update_series_after_appointment_change(series)

        if canceled:
            cls._queue_notifications(canceled)
        return canceled

    @classmethod
    def _update_series_after_appointment_change(cls, series: AppointmentSeries):
        if series.status != AppointmentSeries.Status.ACTIVE:
            return

        today = timezone.localdate()
        scheduled_future = series.appointments.filter(
            status=Appointment.Status.SCHEDULED,
            appointment_date__gte=today,
        ).exists()

        if scheduled_future:
            return

        if not series.is_recurring:
            has_canceled = series.appointments.filter(
                status=Appointment.Status.CANCELED
            ).exists()
            if has_canceled and not series.appointments.filter(
                status=Appointment.Status.SCHEDULED
            ).exists():
                series.status = AppointmentSeries.Status.CANCELED
                series.save(update_fields=["status"])
            return

        all_completed = (
            series.appointments.exists()
            and not series.appointments.exclude(
                status=Appointment.Status.COMPLETED
            ).exists()
        )
        if all_completed:
            series.status = AppointmentSeries.Status.ENDED
            series.save(update_fields=["status"])

    @classmethod
    def mark_completed(cls, appointment: Appointment):
        if appointment.status != Appointment.Status.SCHEDULED:
            return appointment

        appointment.status = Appointment.Status.COMPLETED
        appointment.save(update_fields=["status"])

        series = appointment.appointment_series
        if series.status != AppointmentSeries.Status.ACTIVE:
            return appointment

        has_scheduled = series.appointments.filter(
            status=Appointment.Status.SCHEDULED
        ).exists()
        if has_scheduled:
            return appointment

        if not series.is_recurring:
            series.status = AppointmentSeries.Status.ENDED
            series.save(update_fields=["status"])
            return appointment

        from reservations.services.generation import AppointmentGenerationService

        horizon_date = AppointmentGenerationService.default_horizon_date()
        latest_date = (
            series.appointments.order_by("-appointment_date")
            .values_list("appointment_date", flat=True)
            .first()
        )
        if latest_date is not None and latest_date >= horizon_date:
            series.status = AppointmentSeries.Status.ENDED
            series.save(update_fields=["status"])
        return appointment
