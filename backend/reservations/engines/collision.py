from datetime import date, time

from reservations.models import Appointment, AppointmentSeries


class CollisionDetectionEngine:
    @staticmethod
    def check(
        therapist_id,
        appointment_date: date,
        start_time: time,
        end_time: time,
        *,
        exclude_appointment_id=None,
    ) -> bool:
        queryset = Appointment.objects.filter(
            therapist_id=therapist_id,
            appointment_date=appointment_date,
            status=Appointment.Status.SCHEDULED,
            appointment_series__status=AppointmentSeries.Status.ACTIVE,
        )
        if exclude_appointment_id is not None:
            queryset = queryset.exclude(id=exclude_appointment_id)

        return queryset.filter(
            appointment_series__start_time__lt=end_time,
            appointment_series__end_time__gt=start_time,
        ).exists()
