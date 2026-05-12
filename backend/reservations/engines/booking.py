from datetime import date, timedelta

from constance import config
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from therapist_availability.engines.availability import AvailabilityEngine
from therapist_availability.utils import exclude_intervals

from reservations.filters import filter_appointments_for_day

from .collision import CollisionDetectionEngine


class BookingEngine:
    @staticmethod
    def _get_bookable_slots(therapist, appointment_date):
        slots = AvailabilityEngine.get_slots(therapist, appointment_date)
        appointment_blocks = [
            {
                "start_time": appointment.appointment_series.start_time,
                "end_time": appointment.appointment_series.end_time,
            }
            for appointment in filter_appointments_for_day(therapist, appointment_date)
        ]
        return exclude_intervals(
            slots, sorted(appointment_blocks, key=lambda item: item["start_time"])
        )

    @classmethod
    def slot_in_availability(cls, therapist, appointment_date, start_time, end_time) -> bool:
        blocks = cls._get_bookable_slots(therapist, appointment_date)
        return any(
            start_time >= block["start_time"] and end_time <= block["end_time"]
            for block in blocks
        )

    @staticmethod
    def validate_booking_date(appointment_date: date):
        today = date.today()
        if appointment_date < today:
            raise ValidationError(_("Nie można rezerwować wizyty w przeszłości."))
        if appointment_date > today + timedelta(days=config.APPOINTMENT_BOOKING_DAYS):
            raise ValidationError(
                _("Nie można rezerwować wizyty ponad określone ramy czasowe")
            )

    @classmethod
    def validate_slot(cls, therapist, appointment_date, start_time, end_time):
        cls.validate_booking_date(appointment_date)

        if not cls.slot_in_availability(therapist, appointment_date, start_time, end_time):
            raise ValidationError(_("Wybrany termin jest niedostępny"))

        if CollisionDetectionEngine.check(
            therapist.id, appointment_date, start_time, end_time
        ):
            raise ValidationError(_("Wybrany termin jest zajęty"))
