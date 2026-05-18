from constance import config
from django.utils import timezone
from rest_framework import status

from reservations.engines.generation import AppointmentGenerationEngine
from reservations.models import AppointmentSeries

from .base import ReservationAPITestCase
from .helpers import future_monday


class ReservationCreateAPITestCase(ReservationAPITestCase):
    def test_duplicate_booking_is_rejected(self):
        target_date = future_monday()
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
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("niedostępny", str(second.data).lower())

    def test_periodic_with_non_periodic_type_returns_400(self):
        target_date = future_monday()
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
        target_date = future_monday()
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
