from datetime import date, timedelta

from constance import config
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from scheduling.engine import generate_daily_availability_blocks
from scheduling.filters import filter_weekly_availability_blocks

from .filters import filter_appointmets_specific_slot


# Validates if provided slot can be scheduled
def check_available_slot(therapist, appointment_date, start_time, end_time):
    blocks = generate_daily_availability_blocks(therapist, appointment_date)

    for block in blocks:
        if start_time >= block["start_time"] and end_time <= block["end_time"]:
            return True
    return False


# Validates if specified one time appointment can be scheduled
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


# Validates if specified periodic appointment can be scheduled
def validate_periodic_appointments(therapist, start_date, start_time, end_time):
    day_of_week = start_date.weekday()

    if filter_weekly_availability_blocks(
        therapist, day_of_week, start_time, end_time
    ).exists():
        raise ValidationError(_("Wybrany termin jest zajęty"))

    # TODO: Validate with other periodic appontments
