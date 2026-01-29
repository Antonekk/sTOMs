from datetime import date, timedelta

from constance import config

from reservations.models import Appointment


def generate_appointments_for_series(appointment_series):
    start_time = date.today()
    end_time = start_time + timedelta(days=config.APPOINTMENT_GENERATION_DAYS)

    existing_dates = set(
        appointment_series.appointments.values_list("appointment_date", flat=True)
    )

    for occurrence in appointment_series.recurrence.between(start_time, end_time):
        if occurrence not in existing_dates:
            Appointment.objects.create(
                appointment_series=appointment_series,
                appointment_date=occurrence,
                final_price=appointment_series.appointment_type.price,
            )
