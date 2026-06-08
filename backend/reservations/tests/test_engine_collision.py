from datetime import time

from reservations.engines.collision import CollisionDetectionEngine
from reservations.models import Appointment, AppointmentSeries

from .base import ReservationAPITestCase
from .helpers import create_appointment, create_series, future_monday


class CollisionDetectionEngineTestCase(ReservationAPITestCase):
    def test_detects_collision_for_scheduled_visit_on_canceled_series(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 30),
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            status=Appointment.Status.SCHEDULED,
        )
        series.status = AppointmentSeries.Status.CANCELED
        series.save(update_fields=["status"])

        has_collision = CollisionDetectionEngine.check(
            self.therapist.id,
            target_date,
            time(10, 0),
            time(10, 30),
        )

        self.assertTrue(has_collision)

    def test_no_collision_for_canceled_visit_on_active_one_time_series(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 30),
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            status=Appointment.Status.CANCELED,
        )

        has_collision = CollisionDetectionEngine.check(
            self.therapist.id,
            target_date,
            time(10, 0),
            time(10, 30),
        )

        self.assertFalse(has_collision)

    def test_no_collision_for_canceled_one_time_series(self):
        target_date = future_monday()
        series = create_series(
            therapist=self.therapist,
            patient=self.patient,
            appointment_type=self.one_time_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 30),
            status=AppointmentSeries.Status.CANCELED,
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
            status=Appointment.Status.CANCELED,
        )

        has_collision = CollisionDetectionEngine.check(
            self.therapist.id,
            target_date,
            time(10, 0),
            time(10, 30),
        )

        self.assertFalse(has_collision)

    def test_collision_for_active_weekly_series_with_canceled_visits(self):
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

        has_collision = CollisionDetectionEngine.has_active_weekly_series_conflict(
            self.therapist.id,
            target_date.weekday(),
            time(10, 0),
            time(10, 30),
        )

        self.assertTrue(has_collision)
