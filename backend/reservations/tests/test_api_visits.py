from datetime import time, timedelta
from unittest.mock import patch

from constance import config
from django.utils import timezone
from rest_framework import status

from reservations.engines.horizon import HorizonEngine
from reservations.models import AppointmentSeries

from .base import ReservationAPITestCase
from .helpers import (
    add_weekly_schedule,
    create_appointment,
    create_client,
    create_series,
    create_therapist,
    future_monday,
)


class VisitAPITestCase(ReservationAPITestCase):
    def test_client_sees_only_own_visits(self):
        other_user, other_patient = create_client("c2@test.com")
        target_date = future_monday()
        other_series = create_series(
            therapist=self.therapist,
            patient=other_patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
        )
        create_appointment(
            series=other_series,
            therapist=self.therapist,
            patient=other_patient,
            appointment_date=target_date,
        )

        own_series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date + timedelta(days=1),
            start_time=time(11, 0),
            end_time=time(11, 30),
        )
        own_appointment = create_appointment(
            series=own_series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=1),
        )

        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/visits")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertIn(str(own_appointment.id), ids)
        self.assertEqual(len(ids), 1)

    def test_therapist_sees_only_assigned_visits(self):
        target_date = future_monday()
        other_user, other_therapist = create_therapist("t2@test.com")
        add_weekly_schedule(other_therapist)

        foreign_series = create_series(
            therapist=other_therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
        )
        create_appointment(
            series=foreign_series,
            therapist=other_therapist,
            patient=self.patient,
            appointment_date=target_date,
        )

        own_series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
            start_time=time(12, 0),
            end_time=time(12, 30),
        )
        own_appointment = create_appointment(
            series=own_series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
        )

        self.api.force_authenticate(user=self.therapist_user)
        response = self.api.get("/api/v1/visits")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data}
        self.assertEqual(ids, {str(own_appointment.id)})

    def test_client_visit_payload_excludes_notes(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            notes="N1",
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/visits")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("notes", response.data[0])

    def test_visit_list_does_not_extend_horizon(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 50),
            is_weekly=True,
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
        )

        self.api.force_authenticate(user=self.client_user)
        original = config.APPOINTMENT_GENERATION_DAYS
        config.APPOINTMENT_GENERATION_DAYS = 21
        try:
            response = self.api.get("/api/v1/visits")
        finally:
            config.APPOINTMENT_GENERATION_DAYS = original
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(series.appointments.count(), 1)

    def test_cancel_within_window_blocked_returns_409(self):
        target_date = timezone.localdate()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
            start_time=time(23, 0),
            end_time=time(23, 30),
        )
        appointment = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
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

    def test_cancel_only_visit_cancels_one_time_series(self):
        target_date = future_monday() + timedelta(days=2)
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
        )
        appointment = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
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

    def test_client_cannot_patch_visit_status(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
        )
        appointment = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/visits/{appointment.id}/status",
            {"status": "COMPLETED"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_last_scheduled_ends_recurring_series(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 50),
        )
        appointment = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
        )
        with patch.object(
            HorizonEngine,
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

    def test_therapist_cancel_below_window_returns_409(self):
        target_date = timezone.localdate()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
            start_time=time(23, 30),
            end_time=time(23, 59),
        )
        appointment = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
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
