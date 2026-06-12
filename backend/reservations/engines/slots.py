from datetime import date, time, timedelta

from constance import config
from django.utils import timezone
from offices.location import serialize_office_location
from therapist_availability.models import Therapist

from .booking import BookingEngine


def _time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def _minutes_to_time(minutes: int) -> time:
    return time(hour=minutes // 60, minute=minutes % 60)


class BookableSlotsEngine:
    @classmethod
    def list_slots(
        cls,
        appointment_type,
        date_from: date,
        date_to: date,
        therapist_id=None,
        office_id=None,
        day_of_week=None,
        time_from: time | None = None,
        time_to: time | None = None,
    ) -> list[dict]:
        duration = appointment_type.duration_time_minutes
        therapists = Therapist.objects.select_related(
            "user", "office", "office__localization"
        )
        if therapist_id:
            therapists = therapists.filter(id=therapist_id)
        if office_id:
            therapists = therapists.filter(office_id=office_id)

        slots: list[dict] = []
        current = date_from
        today = timezone.localdate()
        max_date = today + timedelta(days=config.APPOINTMENT_BOOKING_DAYS)

        while current <= date_to:
            if current < today or current > max_date:
                current += timedelta(days=1)
                continue

            if day_of_week is not None and current.weekday() != int(day_of_week):
                current += timedelta(days=1)
                continue

            for therapist in therapists:
                intervals = BookingEngine._get_bookable_slots(therapist, current)
                for interval in intervals:
                    cursor = _time_to_minutes(interval["start_time"])
                    interval_end = _time_to_minutes(interval["end_time"])

                    while cursor + duration <= interval_end:
                        slot_start = _minutes_to_time(cursor)
                        slot_end = _minutes_to_time(cursor + duration)

                        if time_from is not None and slot_start < time_from:
                            cursor += duration
                            continue
                        if time_to is not None and slot_end > time_to:
                            break
                        if BookingEngine.is_past_slot(current, slot_start):
                            cursor += duration
                            continue

                        office = therapist.office

                        slots.append(
                            {
                                "therapist_id": therapist.id,
                                "therapist_name": therapist.user.get_full_name(),
                                "office_id": office.id if office else None,
                                "office": serialize_office_location(office),
                                "date": current,
                                "start_time": slot_start,
                                "end_time": slot_end,
                            }
                        )
                        cursor += duration

            current += timedelta(days=1)

        return sorted(slots, key=lambda item: (item["date"], item["start_time"]))
