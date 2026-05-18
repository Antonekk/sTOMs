from datetime import time

from django.test import TestCase
from therapist_availability.models import AvailabilityBlock

from reservations.engines.cancellation import CancellationEngine
from reservations.models import Appointment

from .helpers import (
    add_weekly_schedule,
    create_appointment,
    create_appointment_types,
    create_client,
    create_series,
    create_therapist,
    future_monday,
)


class CancellationEngineTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("t3@test.com")
        _, cls.patient = create_client("c3@test.com")
        cls.periodic_type, cls.one_time_type = create_appointment_types()
        add_weekly_schedule(cls.therapist)

    def test_cancel_conflicting_appointments_without_window(self):
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

        AvailabilityBlock.objects.filter(therapist=self.therapist).delete()
        canceled = CancellationEngine.cancel_conflicting_appointments(
            self.therapist, target_date
        )
        appointment.refresh_from_db()
        self.assertEqual(len(canceled), 1)
        self.assertEqual(appointment.status, Appointment.Status.CANCELED)
