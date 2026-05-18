from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from notifications.models import Notification
from notifications.tasks import send_appointment_reminders

from .helpers import create_client, create_series, create_therapist


class AppointmentReminderTaskTestCase(TestCase):
    def setUp(self):
        self.therapist_user, self.therapist = create_therapist()
        self.client_user, self.patient = create_client()
        self.series, self.appointment, _ = create_series(
            therapist=self.therapist,
            patient=self.patient,
        )

    def _freeze_at(self, frozen_at):
        if timezone.is_naive(frozen_at):
            frozen_at = timezone.make_aware(frozen_at)
        return patch(
            "notifications.tasks.timezone.now",
            return_value=frozen_at,
        )

    def test_send_appointment_reminders_creates_notification_once(self):
        appointment_start = timezone.make_aware(datetime(2026, 6, 8, 10, 0))
        remind_at = appointment_start - timedelta(hours=24)
        self.appointment.appointment_date = appointment_start.date()
        self.appointment.save(update_fields=["appointment_date"])
        self.series.start_time = appointment_start.time()
        self.series.save(update_fields=["start_time"])

        with self._freeze_at(remind_at + timedelta(minutes=30)):
            send_appointment_reminders()

        self.assertEqual(Notification.objects.filter(user=self.client_user).count(), 1)
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.reminder_sent)

        with self._freeze_at(remind_at + timedelta(hours=1)):
            send_appointment_reminders()

        self.assertEqual(Notification.objects.filter(user=self.client_user).count(), 1)

    def test_send_appointment_reminders_waits_until_remind_at(self):
        appointment_start = timezone.make_aware(datetime(2026, 6, 8, 10, 0))
        remind_at = appointment_start - timedelta(hours=24)
        self.appointment.appointment_date = appointment_start.date()
        self.appointment.save(update_fields=["appointment_date"])
        self.series.start_time = appointment_start.time()
        self.series.save(update_fields=["start_time"])

        with self._freeze_at(remind_at - timedelta(minutes=1)):
            send_appointment_reminders()

        self.assertEqual(Notification.objects.count(), 0)
        self.appointment.refresh_from_db()
        self.assertFalse(self.appointment.reminder_sent)
