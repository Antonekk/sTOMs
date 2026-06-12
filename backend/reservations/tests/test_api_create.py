from datetime import datetime, time
from unittest.mock import patch

from constance import config
from django.utils import timezone
from rest_framework import status

from reservations.engines.generation import AppointmentGenerationEngine
from reservations.engines.horizon import HorizonEngine
from reservations.models import Appointment, AppointmentSeries

from .base import ReservationAPITestCase
from .helpers import create_appointment, create_series, future_monday


class ReservationCreateAPITestCase(ReservationAPITestCase):
    @patch("reservations.engines.booking.timezone.now")
    def test_booking_past_time_today_returns_400(self, mock_now):
        today = timezone.localdate()
        mock_now.return_value = timezone.make_aware(
            datetime.combine(today, time(14, 0))
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.post(
            "/api/v1/reservations",
            {
                "therapist_id": str(self.therapist.id),
                "patient_id": str(self.patient.id),
                "appointment_type_id": str(self.one_time_type.id),
                "start_time": "10:00",
                "start_date": today.isoformat(),
                "is_weekly": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("przeszłości", str(response.data).lower())

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

    def test_periodic_reservation_rejected_when_active_series_has_canceled_visits(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 30),
            is_weekly=True,
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            status=Appointment.Status.CANCELED,
        )

        self.api.force_authenticate(user=self.client_user)
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("koliduje", str(response.data).lower())

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
                HorizonEngine.default_horizon_date(),
            )
        )
        self.assertEqual(series.appointments.count(), expected_count)
        self.assertGreater(expected_count, 1)
