from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from offices.models import Localization, Office
from patients.models import Patient
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import Notification
from notifications.services import CanceledBy, NotificationService
from notifications.tasks import send_appointment_reminders
from notifications.templating import render_notification
from reservations.models import Appointment, AppointmentSeries, AppointmentType
from therapist_availability.models import Therapist

User = get_user_model()


def _unique_phone(email: str) -> str:
    suffix = abs(hash(email)) % 900_000_000 + 100_000_000
    return f"+48{suffix}"


def create_therapist(email="therapist@test.com"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number=_unique_phone(email),
        first_name="Jan",
        last_name="Nowak",
        role=User.Role.THERAPIST,
    )
    localization = Localization.objects.create(
        name=f"Lokalizacja {email}",
        city="Warszawa",
        postal_code="00-001",
        address="ul. Testowa 1",
    )
    office = Office.objects.create(localization=localization, room_number="101")
    therapist = Therapist.objects.create(user=user, office=office)
    return user, therapist


def create_client(email="client@test.com"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number=_unique_phone(email),
        first_name="Katarzyna",
        last_name="Klient",
        role=User.Role.CLIENT,
    )
    patient = Patient.objects.create(
        user=user,
        first_name="Tomasz",
        last_name="Kowalski",
        date_of_birth=date(2018, 4, 15),
        is_primary=True,
    )
    return user, patient


def create_series(*, therapist, patient, is_weekly=False):
    appointment_type = AppointmentType.objects.create(
        name=f"Zajęcia logopedyczne {patient.id}",
        duration_time_minutes=50,
        price="150.00",
        is_periodic=is_weekly,
    )
    target_date = timezone.localdate() + timedelta(days=7)
    series = AppointmentSeries.objects.create(
        therapist=therapist,
        patient=patient,
        appointment_type=appointment_type,
        start_time=time(10, 0),
        end_time=time(10, 50),
        start_date=target_date,
        is_weekly=is_weekly,
    )
    appointment = Appointment.objects.create(
        appointment_series=series,
        therapist=therapist,
        patient=patient,
        appointment_date=target_date,
        final_price=appointment_type.price,
    )
    return series, appointment, appointment_type


class NotificationServiceTestCase(TestCase):
    def setUp(self):
        self.therapist_user, self.therapist = create_therapist()
        self.client_user, self.patient = create_client()
        self.series, self.appointment, _ = create_series(
            therapist=self.therapist,
            patient=self.patient,
        )

    def test_notify_reservation_created_creates_two_notifications(self):
        NotificationService.notify_reservation_created(self.series)
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
        NotificationService.notify_appointment_canceled(self.appointment, CanceledBy.CLIENT)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()
        self.assertEqual(notification.user, self.therapist_user)
        self.assertEqual(notification.title, "Wizyta odwołana przez klienta")

    def test_notify_appointment_canceled_by_therapist_notifies_client_only(self):
        NotificationService.notify_appointment_canceled(
            self.appointment,
            CanceledBy.THERAPIST,
        )
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()
        self.assertEqual(notification.user, self.client_user)
        self.assertEqual(notification.title, "Wizyta odwołana")

    def test_notify_appointments_canceled_bulk(self):
        client_user_2, patient_2 = create_client("client2@test.com")
        _, appointment_2, _ = create_series(
            therapist=self.therapist,
            patient=patient_2,
        )
        NotificationService.notify_appointments_canceled_bulk(
            [self.appointment, appointment_2],
            self.therapist,
        )
        self.assertEqual(Notification.objects.filter(user=self.client_user).count(), 1)
        self.assertEqual(Notification.objects.filter(user=client_user_2).count(), 1)
        therapist_notification = Notification.objects.get(user=self.therapist_user)
        self.assertEqual(therapist_notification.title, "Wizyty anulowane po zmianie grafiku")
        self.assertIn("Automatycznie anulowano 2 wizyt", therapist_notification.description)


class NotificationAPITestCase(APITestCase):
    def setUp(self):
        self.therapist_user, self.therapist = create_therapist()
        self.client_user, self.patient = create_client()
        self.other_user, _ = create_client("other@test.com")
        self.api = APIClient()

        self.client_notification = Notification.objects.create(
            user=self.client_user,
            title="Powiadomienie klienta",
            description="Treść klienta",
        )
        self.other_notification = Notification.objects.create(
            user=self.other_user,
            title="Powiadomienie innego użytkownika",
            description="Treść innego użytkownika",
        )

    def test_list_returns_only_own_notifications(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/notifications")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.client_notification.id))

    def test_mark_read_other_user_notification_returns_404(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/notifications/{self.other_notification.id}/read"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_notification.refresh_from_db()
        self.assertFalse(self.other_notification.is_read)

    def test_mark_all_read_updates_only_authenticated_user_notifications(self):
        Notification.objects.create(
            user=self.client_user,
            title="Drugie powiadomienie",
            description="Nieprzeczytane",
            is_read=False,
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch("/api/v1/notifications/read")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Notification.objects.filter(user=self.client_user, is_read=False).exists()
        )
        self.other_notification.refresh_from_db()
        self.assertFalse(self.other_notification.is_read)

    def test_mark_single_notification_as_read(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/notifications/{self.client_notification.id}/read"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_notification.refresh_from_db()
        self.assertTrue(self.client_notification.is_read)


class AppointmentReminderTaskTestCase(TestCase):
    def setUp(self):
        self.therapist_user, self.therapist = create_therapist()
        self.client_user, self.patient = create_client()
        self.series, self.appointment, _ = create_series(
            therapist=self.therapist,
            patient=self.patient,
        )

    def test_send_appointment_reminders_creates_notification_once(self):
        reminder_date = timezone.localdate() + timedelta(days=1)
        self.appointment.appointment_date = reminder_date
        self.appointment.save(update_fields=["appointment_date"])
        self.series.start_time = time(10, 0)
        self.series.save(update_fields=["start_time"])

        send_appointment_reminders()
        self.assertEqual(Notification.objects.filter(user=self.client_user).count(), 1)
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.reminder_sent)

        send_appointment_reminders()
        self.assertEqual(Notification.objects.filter(user=self.client_user).count(), 1)

    def test_send_appointment_reminders_skips_outside_window(self):
        self.appointment.appointment_date = timezone.localdate() + timedelta(days=10)
        self.appointment.save(update_fields=["appointment_date"])

        send_appointment_reminders()
        self.assertEqual(Notification.objects.count(), 0)


class NotificationTemplateTestCase(TestCase):
    def test_all_notification_templates_render(self):
        base_context = {
            "appointment_type": "Zajęcia logopedyczne",
            "start_time": "10:00",
            "appointment_date": "2025-09-01",
            "start_date": "2025-09-01",
            "weekday": "poniedziałek",
            "patient_name": "Tomasz Kowalski",
            "localization_name": "Gabinet centrum",
            "room_number": "101",
            "count": 2,
            "dates_display": "2025-09-01, 2025-09-08",
        }
        template_paths = [
            "reservation_created/client_one_time",
            "reservation_created/client_recurring",
            "reservation_created/therapist_one_time",
            "reservation_created/therapist_recurring",
            "appointment_canceled_by_client",
            "appointment_canceled_by_therapist",
            "series_canceled_by_client",
            "appointment_auto_canceled",
            "appointments_bulk_auto_canceled",
            "upcoming_appointment",
        ]
        for template_path in template_paths:
            with self.subTest(template_path=template_path):
                title, description = render_notification(template_path, base_context)
                self.assertTrue(title)
                self.assertTrue(description)
