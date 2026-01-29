from django.utils import timezone

from reservations.engine import (
    validate_one_time_appointment,
    validate_periodic_appointments,
)
from reservations.models import Appointment, AppointmentSeries


def book_single_appointment(
    therapist,
    patient,
    appointment_type,
    date,
    start_time,
):
    end_time = (
        timezone.datetime.combine(date, start_time)
        + timezone.timedelta(minutes=appointment_type.duration_time_minutes)
    ).time()

    validate_one_time_appointment(
        therapist,
        date,
        start_time,
        end_time,
    )

    series = AppointmentSeries.objects.create(
        therapist=therapist,
        patient=patient,
        appointment_type=appointment_type,
        start_time=start_time,
        end_time=end_time,
        start_date=date,
        is_weekly=False,
    )

    Appointment.objects.create(
        appointment_series=series,
        appointment_date=date,
        final_price=appointment_type.price,
    )

    return series


def book_periodic_appointment(
    therapist,
    patient,
    appointment_type,
    start_date,
    start_time,
):
    end_time = (
        timezone.datetime.combine(timezone.now(), start_time)
        + timezone.timedelta(minutes=appointment_type.duration_time_minutes)
    ).time()

    validate_periodic_appointments(
        therapist,
        start_date,
        start_time,
        end_time,
    )

    return AppointmentSeries.objects.create(
        therapist=therapist,
        patient=patient,
        appointment_type=appointment_type,
        start_date=start_date,
        is_weekly=True,
        start_time=start_time,
        end_time=end_time,
    )
