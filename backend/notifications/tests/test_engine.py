from django.test import TestCase

from notifications.engine import CanceledBy, NotificationEngine
from notifications.models import Notification

from .helpers import create_client, create_series, create_therapist


class NotificationEngineTestCase(TestCase):
    def setUp(self):
        self.therapist_user, self.therapist = create_therapist()
        self.client_user, self.patient = create_client()
        self.series, self.appointment, _ = create_series(
            therapist=self.therapist,
            patient=self.patient,
        )

    def test_notify_reservation_created_creates_two_notifications(self):
        NotificationEngine.notify_reservation_created(self.series)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertTrue(
            Notification.objects.filter(
                user=self.client_user,
                title="Rezerwacja potwierdzona",
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                user=self.therapist_user,
                title="Nowa rezerwacja",
            ).exists()
        )

    def test_notify_appointment_canceled_by_client_notifies_therapist_only(self):
        NotificationEngine.notify_appointment_canceled(self.appointment, CanceledBy.CLIENT)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()
        self.assertEqual(notification.user, self.therapist_user)
        self.assertEqual(notification.title, "Wizyta odwołana przez klienta")

    def test_notify_appointment_canceled_by_therapist_notifies_client_only(self):
        NotificationEngine.notify_appointment_canceled(
            self.appointment,
            CanceledBy.THERAPIST,
        )
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()
        self.assertEqual(notification.user, self.client_user)
        self.assertEqual(notification.title, "Wizyta odwołana")

    def test_notify_appointments_canceled_bulk(self):
        client_user_2, patient_2 = create_client("c2@test.com")
        _, appointment_2, _ = create_series(
            therapist=self.therapist,
            patient=patient_2,
        )
        NotificationEngine.notify_appointments_canceled_bulk(
            [self.appointment, appointment_2],
            self.therapist,
        )
        self.assertEqual(Notification.objects.filter(user=self.client_user).count(), 1)
        self.assertEqual(Notification.objects.filter(user=client_user_2).count(), 1)
        therapist_notification = Notification.objects.get(user=self.therapist_user)
        self.assertEqual(therapist_notification.title, "Wizyty anulowane po zmianie grafiku")
        self.assertIn("Automatycznie anulowano 2 wizyt", therapist_notification.description)
