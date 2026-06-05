from celery import shared_task

from reservations.engines.horizon import HorizonEngine
from reservations.models import AppointmentSeries


@shared_task(name="reservations.tasks.extend_appointment_horizons")
def extend_appointment_horizons():
    queryset = AppointmentSeries.objects.filter(status=AppointmentSeries.Status.ACTIVE)
    HorizonEngine.ensure_for_queryset(queryset)
