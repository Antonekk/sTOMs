from datetime import time, timedelta

from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist, next_monday


class ScheduleOverrideAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist("t2@test.com")
        cls.other_user, cls.other_therapist = create_therapist("t3@test.com")
        cls.monday = next_monday()
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.therapist_user)

    def test_create_exclusion(self):
        response = self.api.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "EXCLUSION",
                "specific_date": self.monday.isoformat(),
                "start_time": "10:00",
                "end_time": "12:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_create_override_past_date_returns_400(self):
        response = self.api.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "EXCLUSION",
                "specific_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "start_time": "10:00",
                "end_time": "11:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_other_therapist_override_returns_404(self):
        exclusion = AvailabilityBlock.objects.create(
            therapist=self.other_therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        response = self.api.delete(
            f"/api/therapists/self/schedule/override/{exclusion.id}"
        )
        self.assertEqual(response.status_code, 404)
