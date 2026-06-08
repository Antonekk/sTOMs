from .models import Appointment


def filter_appointments_for_day(therapist, appointment_date):
    return Appointment.objects.filter(
        therapist=therapist,
        appointment_date=appointment_date,
        status=Appointment.Status.SCHEDULED,
    ).order_by("appointment_series__start_time")
