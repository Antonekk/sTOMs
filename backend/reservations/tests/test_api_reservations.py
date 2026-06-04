from datetime import time, timedelta

from constance import config
from django.utils import timezone
from rest_framework import status

from reservations.models import Appointment, AppointmentSeries

from .base import ReservationAPITestCase
from .helpers import create_appointment, create_series, future_monday


class ReservationDetailAPITestCase(ReservationAPITestCase):
    def test_reservation_detail_includes_office(self):
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
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get(f"/api/v1/reservations/{series.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["office"]["address"], "Addr")
        self.assertEqual(response.data["office"]["room_number"], "101")

    def test_cancel_series_cancels_future_not_completed(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 50),
            is_weekly=False,
        )
        past = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date - timedelta(days=7),
            status=Appointment.Status.COMPLETED,
        )
        future = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
            status=Appointment.Status.SCHEDULED,
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

    def test_cancel_series_leaves_visit_within_cancellation_window(self):
        target_date = timezone.localdate()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.periodic_type,
            start_date=target_date,
            start_time=time(23, 0),
            end_time=time(23, 50),
            is_weekly=True,
        )
        within_window = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            status=Appointment.Status.SCHEDULED,
        )
        cancelable = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
            status=Appointment.Status.SCHEDULED,
        )

        self.api.force_authenticate(user=self.client_user)
        original = config.CANCELLATION_WINDOW_HOURS
        config.CANCELLATION_WINDOW_HOURS = 24
        try:
            response = self.api.patch(
                f"/api/v1/reservations/{series.id}",
                {"status": "CANCELED"},
                format="json",
            )
        finally:
            config.CANCELLATION_WINDOW_HOURS = original

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        series.refresh_from_db()
        within_window.refresh_from_db()
        cancelable.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.CANCELED)
        self.assertEqual(within_window.status, Appointment.Status.SCHEDULED)
        self.assertEqual(cancelable.status, Appointment.Status.CANCELED)
