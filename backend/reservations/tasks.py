from celery import shared_task

from reservations.engines.horizon import ensure_horizon_for_queryset
from reservations.models import AppointmentSeries


@shared_task(name="reservations.tasks.extend_appointment_horizons")
def extend_appointment_horizons():
    queryset = AppointmentSeries.objects.filter(status=AppointmentSeries.Status.ACTIVE)
    ensure_horizon_for_queryset(queryset)
