from dataclasses import dataclass
from datetime import date, time, timedelta

from constance import config
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import AppointmentType


@dataclass
class SlotSearchParams:
    appointment_type: AppointmentType
    date_from: date
    date_to: date
    therapist_id: str | None
    office_id: str | None
    day_of_week: int | None
    time_from: time | None
    time_to: time | None


def parse_date(value, default: date) -> date:
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(
            {"date": "Nieprawidłowy format daty (YYYY-MM-DD)."}
        ) from exc


def parse_time(value) -> time | None:
    if not value:
        return None
    try:
        if len(value) == 5:
            return time.fromisoformat(f"{value}:00")
        return time.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(
            {"time": "Nieprawidłowy format czasu (HH:MM)."}
        ) from exc


def parse_slot_search_params(
    query_params,
    *,
    include_time_filters: bool = True,
) -> SlotSearchParams:
    appointment_type_id = query_params.get("appointment_type_id")
    if not appointment_type_id:
        raise ValidationError(
            {"appointment_type_id": "Ten parametr jest wymagany."}
        )

    appointment_type = get_object_or_404(AppointmentType, id=appointment_type_id)
    today = timezone.localdate()
    date_from = parse_date(query_params.get("date_from"), today)
    date_to = parse_date(
        query_params.get("date_to"),
        today + timedelta(days=config.APPOINTMENT_BOOKING_DAYS),
    )

    if date_from > date_to:
        raise ValidationError(
            {"date_to": "Data końcowa musi być po dacie początkowej."}
        )

    max_date = today + timedelta(days=config.APPOINTMENT_BOOKING_DAYS)
    if date_from < today:
        raise ValidationError(
            {"date_from": "Data początkowa nie może być w przeszłości."}
        )
    if date_to > max_date:
        raise ValidationError(
            {
                "date_to": (
                    f"Maksymalna data rezerwacji to {max_date.isoformat()}."
                )
            }
        )

    max_days = getattr(config, "AVAILABILITY_MAX_RANGE_DAYS", 14)
    if (date_to - date_from).days > max_days:
        raise ValidationError(
            {"date_to": f"Maksymalny zakres zapytań to {max_days} dni."}
        )

    day_of_week = query_params.get("day_of_week")
    if day_of_week is not None:
        day_of_week = int(day_of_week)
        if day_of_week < 0 or day_of_week > 6:
            raise ValidationError(
                {"day_of_week": "Dzień tygodnia musi być w zakresie 0–6."}
            )

    return SlotSearchParams(
        appointment_type=appointment_type,
        date_from=date_from,
        date_to=date_to,
        therapist_id=query_params.get("therapist_id"),
        office_id=query_params.get("office_id"),
        day_of_week=day_of_week,
        time_from=parse_time(query_params.get("time_from"))
        if include_time_filters
        else None,
        time_to=parse_time(query_params.get("time_to"))
        if include_time_filters
        else None,
    )
