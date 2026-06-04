from datetime import time, timedelta

from constance import config
from django.test import TestCase
from django.utils import timezone
from therapist_availability.models import AvailabilityBlock

from reservations.engines.cancellation import CancellationEngine
from reservations.engines.generation import AppointmentGenerationEngine
from reservations.models import Appointment, AppointmentSeries

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

    def test_cancel_conflicting_appointments_cancels_when_outside_window(self):
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

    def test_cancel_conflicting_appointments_respects_cancellation_window(self):
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

        AvailabilityBlock.objects.filter(therapist=self.therapist).delete()
        original = config.CANCELLATION_WINDOW_HOURS
        config.CANCELLATION_WINDOW_HOURS = 24
        try:
            canceled = CancellationEngine.cancel_conflicting_appointments(
                self.therapist, target_date
            )
        finally:
            config.CANCELLATION_WINDOW_HOURS = original

        appointment.refresh_from_db()
        self.assertEqual(canceled, [])
        self.assertEqual(appointment.status, Appointment.Status.SCHEDULED)

    def test_cancel_conflicting_schedule_change_cancels_non_fitting_series(self):
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
        first = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
        )
        second = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
        )

        AvailabilityBlock.objects.filter(therapist=self.therapist).delete()
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=target_date.weekday(),
            start_time=time(14, 0),
            end_time=time(17, 0),
        )

        canceled = CancellationEngine.cancel_conflicting_appointments(self.therapist)

        series.refresh_from_db()
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.CANCELED)
        self.assertEqual(first.status, Appointment.Status.CANCELED)
        self.assertEqual(second.status, Appointment.Status.CANCELED)
        self.assertEqual(len(canceled), 2)

    def test_cancel_conflicting_schedule_change_respects_cancellation_window(self):
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
        )
        cancelable = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
        )

        AvailabilityBlock.objects.filter(therapist=self.therapist).delete()

        original = config.CANCELLATION_WINDOW_HOURS
        config.CANCELLATION_WINDOW_HOURS = 24
        try:
            CancellationEngine.cancel_conflicting_appointments(self.therapist)
        finally:
            config.CANCELLATION_WINDOW_HOURS = original

        series.refresh_from_db()
        within_window.refresh_from_db()
        cancelable.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.CANCELED)
        self.assertEqual(within_window.status, Appointment.Status.SCHEDULED)
        self.assertEqual(cancelable.status, Appointment.Status.CANCELED)

    def test_cancel_series_respects_cancellation_window(self):
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
        )
        cancelable = create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
        )

        original = config.CANCELLATION_WINDOW_HOURS
        config.CANCELLATION_WINDOW_HOURS = 24
        try:
            CancellationEngine.cancel_series(series)
        finally:
            config.CANCELLATION_WINDOW_HOURS = original

        series.refresh_from_db()
        within_window.refresh_from_db()
        cancelable.refresh_from_db()
        self.assertEqual(series.status, AppointmentSeries.Status.CANCELED)
        self.assertEqual(within_window.status, Appointment.Status.SCHEDULED)
        self.assertEqual(cancelable.status, Appointment.Status.CANCELED)

    def test_cancel_series_stops_weekly_generation(self):
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
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date,
        )
        create_appointment(
            series=series,
            therapist=self.therapist,
            patient=self.patient,
            appointment_date=target_date + timedelta(days=7),
        )

        original_window = config.CANCELLATION_WINDOW_HOURS
        original_horizon = config.APPOINTMENT_GENERATION_DAYS
        config.CANCELLATION_WINDOW_HOURS = 24
        config.APPOINTMENT_GENERATION_DAYS = 28
        try:
            CancellationEngine.cancel_series(series)
            count_after_cancel = series.appointments.count()
            AppointmentGenerationEngine.generate(series)
        finally:
            config.CANCELLATION_WINDOW_HOURS = original_window
            config.APPOINTMENT_GENERATION_DAYS = original_horizon

        self.assertEqual(series.appointments.count(), count_after_cancel)
