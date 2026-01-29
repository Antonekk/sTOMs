from .models import Appointment, AppointmentSeries


def filter_appointments_for_day(therapist, date):
    return Appointment.objects.filter(
        appointment_series__therapist=therapist,
        appointment_date=date,
        appointment_series__status=AppointmentSeries.Status.ACTIVE,
        status=Appointment.Status.SCHEDULED,
    ).order_by("appointment_series__start_time")


def filter_active_appointment_series(therapist):
    return AppointmentSeries.objects.filter(
        therapist=therapist, status=AppointmentSeries.Status.ACTIVE
    )


def filter_appointmets_specific_slot(therapist, appointment_date, start_time, end_time):
    return Appointment.objects.filter(
        appointment_series__therapist=therapist,
        appointment_date=appointment_date,
        status=Appointment.Status.SCHEDULED,
        appointment_series__status=AppointmentSeries.Status.ACTIVE,
        appointment_series__start_time__lt=end_time,
        appointment_series__end_time__gt=start_time,
    )
