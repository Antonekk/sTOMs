from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from reservations.engines.horizon import HorizonEngine
from reservations.models import Appointment, AppointmentSeries


class AppointmentGenerationEngine:
    @staticmethod
    def _occurrence_dates(
        series: AppointmentSeries, range_start: date, horizon_date: date
    ) -> list[date]:
        if not series.is_weekly:
            if series.start_date >= range_start and series.start_date <= horizon_date:
                return [series.start_date]
            return []

        target_weekday = series.start_date.weekday()
        days_ahead = (target_weekday - range_start.weekday()) % 7
        cursor = range_start + timedelta(days=days_ahead)

        dates = []
        while cursor <= horizon_date:
            if cursor >= series.start_date:
                dates.append(cursor)
            cursor += timedelta(days=7)

        return dates

    @classmethod
    @transaction.atomic
    def generate(cls, series: AppointmentSeries, horizon_date: date | None = None) -> list[Appointment]:
        if series.status != AppointmentSeries.Status.ACTIVE:
            return []

        if horizon_date is None:
            horizon_date = HorizonEngine.default_horizon_date()
        range_start = max(series.start_date, timezone.localdate())
        if range_start > horizon_date:
            return []

        existing_dates = set(
            series.appointments.values_list("appointment_date", flat=True)
        )
        created = []

        occurrence_dates = cls._occurrence_dates(series, range_start, horizon_date)
        for occurrence_date in occurrence_dates:
            if occurrence_date in existing_dates:
                continue
            appointment = Appointment.objects.create(
                appointment_series=series,
                therapist=series.therapist,
                patient=series.patient,
                appointment_date=occurrence_date,
                final_price=series.appointment_type.price,
            )
            created.append(appointment)
            existing_dates.add(occurrence_date)

        return created