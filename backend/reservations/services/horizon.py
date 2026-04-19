from reservations.models import AppointmentSeries
from reservations.services.generation import AppointmentGenerationService


def ensure_horizon(series: AppointmentSeries) -> None:
    if series.status != AppointmentSeries.Status.ACTIVE:
        return
    horizon_date = AppointmentGenerationService.default_horizon_date()
    latest = (
        series.appointments.order_by("-appointment_date")
        .values_list("appointment_date", flat=True)
        .first()
    )
    if latest is None or latest < horizon_date:
        AppointmentGenerationService.generate(series, horizon_date)


def ensure_horizon_for_queryset(queryset) -> None:
    for series in queryset.filter(status=AppointmentSeries.Status.ACTIVE):
        ensure_horizon(series)
