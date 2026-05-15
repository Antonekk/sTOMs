from datetime import date, time, timedelta
from constance import config
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from offices.models import Localization, Office
from patients.models import Patient
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from therapist_availability.models import AvailabilityBlock, Therapist
from therapist_availability.engines import ScheduleEngine

from reservations.models import Appointment, AppointmentSeries, AppointmentType
from reservations.engines.cancellation import CancellationEngine
from reservations.engines.generation import AppointmentGenerationEngine
from reservations.engines.horizon import ensure_horizon

User = get_user_model()


def create_therapist(email="therapist@test.com"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number="+48123456789",
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
        phone_number="+48987654321",
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


def create_appointment_types():
    periodic = AppointmentType.objects.create(
        name="Zajęcia logopedyczne",
        duration_time_minutes=50,
        price="150.00",
        is_periodic=True,
    )
    one_time = AppointmentType.objects.create(
        name="Konsultacja",
        duration_time_minutes=30,
        price="100.00",
        is_periodic=False,
    )
    return periodic, one_time


def add_weekly_schedule(therapist):
    ScheduleEngine.replace_base_schedule(
        therapist,
        [
            {"day_of_week": day, "start_time": time(9, 0), "end_time": time(17, 0)}
            for day in range(7)
        ],
    )


class ReservationAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist()
        cls.client_user, cls.patient = create_client()
        cls.periodic_type, cls.one_time_type = create_appointment_types()
        add_weekly_schedule(cls.therapist)

    def setUp(self):
        self.api = APIClient()

    def _future_monday(self):
        today = timezone.localdate()
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)

    def test_collision_returns_409(self):
        target_date = self._future_monday()
        self.api.force_authenticate(user=self.client_user)
        payload = {
            "therapist_id": str(self.therapist.id),
            "patient_id": str(self.patient.id),
            "appointment_type_id": str(self.one_time_type.id),
            "start_time": "10:00",
            "start_date": target_date.isoformat(),
            "is_weekly": False,
        }
        first = self.api.post("/api/v1/reservations", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.api.post("/api/v1/reservations", payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)

    def test_periodic_with_non_periodic_type_returns_400(self):
        target_date = self._future_monday()
        self.api.force_authenticate(user=self.client_user)
        response = self.api.post(
            "/api/v1/reservations",
            {
                "therapist_id": str(self.therapist.id),
                "patient_id": str(self.patient.id),
                "appointment_type_id": str(self.one_time_type.id),
                "start_time": "10:00",
                "start_date": target_date.isoformat(),
                "is_weekly": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_periodic_reservation_generates_appointments_to_horizon(self):
        target_date = self._future_monday()
        self.api.force_authenticate(user=self.client_user)
        original = config.APPOINTMENT_GENERATION_DAYS
        config.APPOINTMENT_GENERATION_DAYS = 14
        try:
            response = self.api.post(
                "/api/v1/reservations",
                {
                    "therapist_id": str(self.therapist.id),
                    "patient_id": str(self.patient.id),
                    "appointment_type_id": str(self.periodic_type.id),
                    "start_time": "10:00",
                    "start_date": target_date.isoformat(),
                    "is_weekly": True,
                },
                format="json",
            )
        finally:
            config.APPOINTMENT_GENERATION_DAYS = original
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        series = AppointmentSeries.objects.get(id=response.data["id"])
        expected_count = len(
            AppointmentGenerationEngine._occurrence_dates(
                series,
                max(series.start_date, timezone.localdate()),
                AppointmentGenerationEngine.default_horizon_date(),
            )
        )
        self.assertEqual(series.appointments.count(), expected_count)
        self.assertGreater(expected_count, 1)

    def test_client_sees_only_own_visits(self):
        other_user, other_patient = create_client("other@test.com")
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=other_patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=other_patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )

        own_series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(11, 0),
            end_time=time(11, 30),
            start_date=target_date + timedelta(days=1),
        )
        own_appointment = Appointment.objects.create(
            appointment_series=own_series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=1),
            final_price=self.one_time_type.price,
        )

        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/visits")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertIn(str(own_appointment.id), ids)
        self.assertEqual(len(ids), 1)

    def test_therapist_sees_only_assigned_visits(self):
        target_date = self._future_monday()
        other_user, other_therapist = create_therapist("other-therapist@test.com")
        add_weekly_schedule(other_therapist)

        foreign_series = AppointmentSeries.objects.create(
            therapist=other_therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        Appointment.objects.create(
            appointment_series=foreign_series,
            therapist=other_therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )

        own_series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(12, 0),
            end_time=time(12, 30),
            start_date=target_date,
        )
        own_appointment = Appointment.objects.create(
            appointment_series=own_series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )

        self.api.force_authenticate(user=self.therapist_user)
        response = self.api.get("/api/v1/visits")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertEqual(ids, {str(own_appointment.id)})

    def test_cancel_within_window_blocked_returns_409(self):
        target_date = timezone.localdate()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(23, 0),
            end_time=time(23, 30),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )

        self.api.force_authenticate(user=self.client_user)
        original = config.CANCELLATION_WINDOW_HOURS
        config.CANCELLATION_WINDOW_HOURS = 24
        try:
            response = self.api.patch(
                f"/api/v1/visits/{appointment.id}/cancel",
                {},
                format="json",
            )
        finally:
            config.CANCELLATION_WINDOW_HOURS = original
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cancel_series_cancels_future_not_completed(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_time=time(10, 0),
            end_time=time(10, 50),
            start_date=target_date,
            is_weekly=False,
        )
        past = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date - timedelta(days=7),
            status=Appointment.Status.COMPLETED,
            final_price=self.periodic_type.price,
        )
        future = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
            status=Appointment.Status.SCHEDULED,
            final_price=self.periodic_type.price,
        )

        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/reservations/{series.id}",
            {"status": "CANCELED"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        series.refresh_from_db()
        past.refresh_from_db()
        future.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.CANCELED)
        self.assertEqual(past.status, Appointment.Status.COMPLETED)
        self.assertEqual(future.status, Appointment.Status.CANCELED)

    def test_client_cannot_patch_visit_status(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/visits/{appointment.id}/status",
            {"status": "COMPLETED"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_last_scheduled_ends_recurring_series(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_time=time(10, 0),
            end_time=time(10, 50),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.periodic_type.price,
        )
        with patch.object(
            AppointmentGenerationEngine,
            "default_horizon_date",
            return_value=target_date,
        ):
            self.api.force_authenticate(user=self.therapist_user)
            response = self.api.patch(
                f"/api/v1/visits/{appointment.id}/status",
                {"status": "COMPLETED"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        series.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.ENDED)

    def test_cancel_only_visit_cancels_one_time_series(self):
        target_date = self._future_monday() + timedelta(days=2)
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/visits/{appointment.id}/cancel",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        series.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.CANCELED)

    def test_therapist_cancel_below_window_returns_409(self):
        target_date = timezone.localdate()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(23, 30),
            end_time=time(23, 59),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )
        self.api.force_authenticate(user=self.therapist_user)
        original = config.CANCELLATION_WINDOW_HOURS
        config.CANCELLATION_WINDOW_HOURS = 24
        try:
            response = self.api.patch(
                f"/api/v1/visits/{appointment.id}/status",
                {"status": "CANCELED"},
                format="json",
            )
        finally:
            config.CANCELLATION_WINDOW_HOURS = original
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_visit_list_extends_horizon(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_time=time(10, 0),
            end_time=time(10, 50),
            start_date=target_date,
            is_weekly=True,
        )
        Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.periodic_type.price,
        )

        self.api.force_authenticate(user=self.client_user)
        original = config.APPOINTMENT_GENERATION_DAYS
        config.APPOINTMENT_GENERATION_DAYS = 21
        try:
            response = self.api.get("/api/v1/visits")
        finally:
            config.APPOINTMENT_GENERATION_DAYS = original
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(series.appointments.count(), 1)

    def test_client_visit_payload_excludes_notes(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
            notes="Tajna notatka",
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/visits")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data[0]
        self.assertNotIn("notes", payload)


class BookableSlotAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist()
        cls.client_user, cls.patient = create_client()
        cls.periodic_type, cls.one_time_type = create_appointment_types()
        add_weekly_schedule(cls.therapist)

    def setUp(self):
        self.api = APIClient()

    def _future_monday(self):
        today = timezone.localdate()
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)

    def _slots_url(self, **params):
        query = {"appointment_type_id": str(self.one_time_type.id), **params}
        return "/api/v1/reservations/slots", query

    def test_bookable_slots_requires_appointment_type(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/reservations/slots")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bookable_slots_returns_paginated_results(self):
        self.api.force_authenticate(user=self.client_user)
        target_date = self._future_monday()
        url, params = self._slots_url(
            date_from=target_date.isoformat(),
            date_to=target_date.isoformat(),
            page_size=5,
        )
        response = self.api.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertGreater(response.data["count"], 5)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

    def test_bookable_slots_excludes_booked_slots(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )

        self.api.force_authenticate(user=self.client_user)
        url, params = self._slots_url(
            date_from=target_date.isoformat(),
            date_to=target_date.isoformat(),
            time_from="10:00",
            time_to="10:30",
        )
        response = self.api.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_bookable_slots_filters_by_time_range(self):
        target_date = self._future_monday()
        self.api.force_authenticate(user=self.client_user)
        url, params = self._slots_url(
            date_from=target_date.isoformat(),
            date_to=target_date.isoformat(),
            time_from="12:00",
            time_to="13:00",
            page_size=100,
        )
        response = self.api.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)
        for slot in response.data["results"]:
            self.assertGreaterEqual(slot["start_time"], "12:00")
            self.assertLessEqual(slot["end_time"], "13:00")

    def test_therapist_list_for_client(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/therapists")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertIn(str(self.therapist.id), ids)
        therapist = next(
            item for item in response.data if item["id"] == str(self.therapist.id)
        )
        self.assertEqual(therapist["office"]["city"], "Warszawa")
        self.assertEqual(therapist["office"]["address"], "ul. Testowa 1")
        self.assertEqual(therapist["office"]["room_number"], "101")

    def test_bookable_slots_include_office_details(self):
        target_date = self._future_monday()
        self.api.force_authenticate(user=self.client_user)
        url, params = self._slots_url(
            date_from=target_date.isoformat(),
            date_to=target_date.isoformat(),
            page_size=1,
        )
        response = self.api.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slot = response.data["results"][0]
        self.assertEqual(slot["office"]["city"], "Warszawa")
        self.assertEqual(slot["office"]["address"], "ul. Testowa 1")
        self.assertEqual(slot["office"]["room_number"], "101")

    def test_time_options_returns_available_hours(self):
        target_date = self._future_monday()
        self.api.force_authenticate(user=self.client_user)
        url, params = self._slots_url(
            date_from=target_date.isoformat(),
            date_to=target_date.isoformat(),
        )
        response = self.api.get(
            "/api/v1/reservations/slots/time-options",
            params,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("09:00", response.data["start_times"])
        self.assertTrue(len(response.data["end_times"]) > 0)


class CancellationEngineTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("cancel@test.com")
        _, cls.patient = create_client("cancel-client@test.com")
        cls.periodic_type, cls.one_time_type = create_appointment_types()
        add_weekly_schedule(cls.therapist)

    def test_cancel_conflicting_appointments_without_window(self):
        target_date = self._future_monday()
        series = AppointmentSeries.objects.create(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_time=time(10, 0),
            end_time=time(10, 30),
            start_date=target_date,
        )
        appointment = Appointment.objects.create(
            appointment_series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            final_price=self.one_time_type.price,
        )

        AvailabilityBlock.objects.filter(therapist=self.therapist).delete()
        canceled = CancellationEngine.cancel_conflicting_appointments(
            self.therapist, target_date
        )
        appointment.refresh_from_db()
        self.assertEqual(len(canceled), 1)
        self.assertEqual(appointment.status, Appointment.Status.CANCELED)

    def _future_monday(self):
        today = timezone.localdate()
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)


class HorizonTestCase(TestCase):
    def test_ensure_horizon_generates_missing_appointments(self):
        _, therapist = create_therapist("horizon@test.com")
        _, patient = create_client("horizon-client@test.com")
        periodic_type, _ = create_appointment_types()
        import recurrence

        target_date = timezone.localdate() + timedelta(days=(0 - timezone.localdate().weekday()) % 7 or 7)
        series = AppointmentSeries.objects.create(
            therapist=therapist,
            patient=patient,
            appointment_type=periodic_type,
            start_time=time(10, 0),
            end_time=time(10, 50),
            start_date=target_date,
            recurrence=recurrence.Recurrence(
                rrules=[recurrence.Rule(recurrence.WEEKLY, byday=recurrence.MO)]
            ),
        )
        original = config.APPOINTMENT_GENERATION_DAYS
        config.APPOINTMENT_GENERATION_DAYS = 28
        try:
            ensure_horizon(series)
        finally:
            config.APPOINTMENT_GENERATION_DAYS = original
        self.assertGreater(series.appointments.count(), 1)
