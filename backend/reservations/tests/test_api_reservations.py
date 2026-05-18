from datetime import time, timedelta

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
