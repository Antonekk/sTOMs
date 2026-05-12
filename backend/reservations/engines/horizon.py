from reservations.models import AppointmentSeries
from reservations.engines.generation import AppointmentGenerationEngine


def ensure_horizon(series: AppointmentSeries) -> None:
    if series.status != AppointmentSeries.Status.ACTIVE:
        return
    horizon_date = AppointmentGenerationEngine.default_horizon_date()
    latest = (
        series.appointments.order_by("-appointment_date")
        .values_list("appointment_date", flat=True)
        .first()
    )
    if latest is None or latest < horizon_date:
        AppointmentGenerationEngine.generate(series, horizon_date)


def ensure_horizon_for_queryset(queryset) -> None:
    for series in queryset.filter(status=AppointmentSeries.Status.ACTIVE):
        ensure_horizon(series)
