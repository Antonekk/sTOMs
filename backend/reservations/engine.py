from datetime import date, timedelta

from constance import config
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from therapist_availability.services.availability import AvailabilityService
from therapist_availability.utils import exclude_intervals

from therapist_availability.models import AvailabilityBlock

from .filters import filter_appointments_for_day, filter_appointmets_specific_slot


def _get_bookable_slots(therapist, appointment_date):
    slots = AvailabilityService.get_slots(therapist, appointment_date)
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


def check_available_slot(therapist, appointment_date, start_time, end_time):
    blocks = _get_bookable_slots(therapist, appointment_date)

    for block in blocks:
        if start_time >= block["start_time"] and end_time <= block["end_time"]:
            return True
    return False


def validate_one_time_appointment(therapist, appointment_date, start_time, end_time):
    if (
        appointment_date
        > date.today() + timedelta(days=config.APPOINTMENT_BOOKING_DAYS)
        or appointment_date < date.today()
    ):
        raise ValidationError(
            _("Nie można rezerwować wizyty ponad określone ramy czasowe")
        )

    if not check_available_slot(therapist, appointment_date, start_time, end_time):
        raise ValidationError(_("Wybrany termin jest niedostępny"))

    if filter_appointmets_specific_slot(
        therapist, appointment_date, start_time, end_time
    ).exists():
        raise ValidationError(_("Wybrany termin jest zajęty"))


def validate_periodic_appointments(therapist, start_date, start_time, end_time):
    day_of_week = start_date.weekday()

    if (
        AvailabilityBlock.objects.filter(
            therapist=therapist,
            day_of_week=day_of_week,
            start_time__lt=end_time,
            end_time__gt=start_time,
            type=AvailabilityBlock.BlockType.BASE,
        ).exists()
    ):
        raise ValidationError(_("Wybrany termin jest zajęty"))

    # TODO: Validate with other periodic appontments
