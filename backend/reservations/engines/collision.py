from datetime import date, time

from django.db.models import Q
from django.db.models.functions import ExtractIsoWeekDay

from reservations.models import Appointment, AppointmentSeries


class CollisionDetectionEngine:
    @staticmethod
    def _time_overlap_filter(start_time: time, end_time: time) -> Q:
        return Q(start_time__lt=end_time, end_time__gt=start_time)

    @classmethod
    def has_active_weekly_series_conflict(
        cls,
        therapist_id,
        weekday: int,
        start_time: time,
        end_time: time,
        exclude_series_id=None,
    ) -> bool:
        queryset = AppointmentSeries.objects.filter(
            therapist_id=therapist_id,
            status=AppointmentSeries.Status.ACTIVE,
            is_weekly=True,
        ).filter(cls._time_overlap_filter(start_time, end_time))
        if exclude_series_id is not None:
            queryset = queryset.exclude(id=exclude_series_id)
        return (
            queryset.annotate(series_weekday=ExtractIsoWeekDay("start_date"))
            .filter(series_weekday=weekday + 1) # +1 because weekday is 0-indexed
            .exists()
        )

    @classmethod
    def _has_active_series_conflict(
        cls,
        therapist_id,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_series_id=None,
    ) -> bool:
        queryset = AppointmentSeries.objects.filter(
            therapist_id=therapist_id,
            status=AppointmentSeries.Status.ACTIVE,
        ).filter(cls._time_overlap_filter(start_time, end_time))
        if exclude_series_id is not None:
            queryset = queryset.exclude(id=exclude_series_id)

        weekday = appointment_date.weekday()
        return (
            queryset.filter(is_weekly=True)
            .annotate(series_weekday=ExtractIsoWeekDay("start_date"))
            .filter(series_weekday=weekday + 1)
            .exists()
        )

    @classmethod
    def check(
        cls,
        therapist_id,
        appointment_date: date,
        start_time: time,
        end_time: time,
        exclude_appointment_id=None,
        exclude_series_id=None,
    ) -> bool:
        queryset = Appointment.objects.filter(
            therapist_id=therapist_id,
            appointment_date=appointment_date,
            status=Appointment.Status.SCHEDULED,
        )
        if exclude_appointment_id is not None:
            queryset = queryset.exclude(id=exclude_appointment_id)

        if queryset.filter(
            appointment_series__start_time__lt=end_time,
            appointment_series__end_time__gt=start_time,
        ).exists():
            return True

        return cls._has_active_series_conflict(
            therapist_id,
            appointment_date,
            start_time,
            end_time,
            exclude_series_id=exclude_series_id,
        )
