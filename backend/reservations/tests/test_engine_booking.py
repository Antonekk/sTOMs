from datetime import date, datetime, time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from reservations.engines.booking import BookingEngine

from .helpers import add_weekly_schedule, create_therapist


class BookingEngineTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist()
        add_weekly_schedule(cls.therapist)

    def test_is_past_slot_true_for_earlier_time_today(self):
        today = date.today()
        fixed_now = timezone.make_aware(datetime.combine(today, time(14, 0)))
        with patch("reservations.engines.booking.timezone.now", return_value=fixed_now):
            self.assertTrue(BookingEngine.is_past_slot(today, time(10, 0)))

    def test_is_past_slot_false_for_later_time_today(self):
        today = date.today()
        fixed_now = timezone.make_aware(datetime.combine(today, time(10, 0)))
        with patch("reservations.engines.booking.timezone.now", return_value=fixed_now):
            self.assertFalse(BookingEngine.is_past_slot(today, time(14, 0)))

    def test_validate_slot_rejects_past_time_today(self):
        today = date.today()
        fixed_now = timezone.make_aware(datetime.combine(today, time(14, 0)))
        with patch("reservations.engines.booking.timezone.now", return_value=fixed_now):
            with self.assertRaises(ValidationError) as context:
                BookingEngine.validate_slot(
                    self.therapist, today, time(10, 0), time(10, 30)
                )
        self.assertIn("przeszłości", str(context.exception).lower())
