from datetime import time

from constance import config
from django.test import TestCase

from reservations.engines.horizon import ensure_horizon
from reservations.tasks import extend_appointment_horizons

from .helpers import (
    create_appointment,
    create_appointment_types,
    create_client,
    create_series,
    create_therapist,
    future_monday,
)


class HorizonEngineTestCase(TestCase):
    def test_ensure_horizon_generates_missing_appointments(self):
        _, therapist = create_therapist("t4@test.com")
        _, patient = create_client("c4@test.com")
        periodic_type, _ = create_appointment_types()

        target_date = future_monday()
        series = create_series(
            therapist=therapist,
            patient=patient,
            appointment_type=periodic_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 50),
            is_weekly=True,
        )
        original = config.APPOINTMENT_GENERATION_DAYS
        config.APPOINTMENT_GENERATION_DAYS = 28
        try:
            ensure_horizon(series)
        finally:
            config.APPOINTMENT_GENERATION_DAYS = original
        self.assertGreater(series.appointments.count(), 1)


class HorizonTaskTestCase(TestCase):
    def test_extend_appointment_horizons_task_generates_missing_appointments(self):
        _, therapist = create_therapist("t5@test.com")
        _, patient = create_client("c5@test.com")
        periodic_type, _ = create_appointment_types()

        target_date = future_monday()
        series = create_series(
            therapist=therapist,
            patient=patient,
            appointment_type=periodic_type,
            start_date=target_date,
            start_time=time(10, 0),
            end_time=time(10, 50),
            is_weekly=True,
        )
        create_appointment(
            series=series,
            therapist=therapist,
            patient=patient,
            appointment_date=target_date,
        )

        original = config.APPOINTMENT_GENERATION_DAYS
        config.APPOINTMENT_GENERATION_DAYS = 28
        try:
            extend_appointment_horizons()
        finally:
            config.APPOINTMENT_GENERATION_DAYS = original
        self.assertGreater(series.appointments.count(), 1)
