from datetime import datetime, time
from unittest.mock import patch

from django.utils import timezone
from rest_framework import status

from .base import ReservationAPITestCase
from .helpers import create_appointment, create_series, future_monday


class BookableSlotAPITestCase(ReservationAPITestCase):
    def _slots_url(self, **params):
        query = {"appointment_type_id": str(self.one_time_type.id), **params}
        return "/api/v1/reservations/slots", query

    def test_bookable_slots_requires_appointment_type(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/reservations/slots")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bookable_slots_returns_paginated_results(self):
        self.api.force_authenticate(user=self.client_user)
        target_date = future_monday()
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
        target_date = future_monday()
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

    def test_bookable_slots_include_office_details(self):
        target_date = future_monday()
        self.api.force_authenticate(user=self.client_user)
        url, params = self._slots_url(
            date_from=target_date.isoformat(),
            date_to=target_date.isoformat(),
            page_size=1,
        )
        response = self.api.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slot = response.data["results"][0]
        self.assertEqual(slot["office"]["city"], "City")
        self.assertEqual(slot["office"]["address"], "Addr")
        self.assertEqual(slot["office"]["room_number"], "101")

    @patch("reservations.engines.booking.timezone.now")
    def test_bookable_slots_excludes_past_times_today(self, mock_now):
        today = timezone.localdate()
        mock_now.return_value = timezone.make_aware(
            datetime.combine(today, time(14, 0))
        )
        self.api.force_authenticate(user=self.client_user)
        url, params = self._slots_url(
            date_from=today.isoformat(),
            date_to=today.isoformat(),
            page_size=100,
        )
        response = self.api.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for slot in response.data["results"]:
            self.assertGreaterEqual(slot["start_time"], "14:00")

    def test_time_options_returns_available_hours(self):
        target_date = future_monday()
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
