from datetime import date, timedelta

from constance import config
from django.utils import timezone

from reservations.models import AppointmentSeries

from reservations.engines.generation import AppointmentGenerationEngine


class HorizonEngine:
    @classmethod
    def default_horizon_date(cls) -> date:
        return timezone.localdate() + timedelta(days=config.APPOINTMENT_GENERATION_DAYS)

    @classmethod
    def ensure(cls, series: AppointmentSeries) -> None:
        if series.status != AppointmentSeries.Status.ACTIVE:
            return
        horizon_date = cls.default_horizon_date()
        latest = (
            series.appointments.order_by("-appointment_date")
            .values_list("appointment_date", flat=True)
            .first()
        )
        if latest is None or latest < horizon_date:
            AppointmentGenerationEngine.generate(series, horizon_date)

    @classmethod
    def ensure_for_queryset(cls, queryset) -> None:
        for series in queryset.filter(status=AppointmentSeries.Status.ACTIVE):
            cls.ensure(series)
