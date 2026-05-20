from datetime import time

from rest_framework.test import APIClient, APITestCase

from therapist_availability.models import AvailabilityBlock

from .helpers import create_client, create_therapist


class ScheduleAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist("t1@test.com")
        cls.client_user = create_client()

    def setUp(self):
        self.api = APIClient()

    def test_get_requires_therapist_role(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/therapists/self/schedule")
        self.assertEqual(response.status_code, 403)

    def test_put_replaces_existing_blocks(self):
        self.api.force_authenticate(user=self.therapist_user)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(8, 0),
            end_time=time(12, 0),
        )
        response = self.api.put(
            "/api/v1/therapists/self/schedule",
            {
                "blocks": [
                    {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 204)
        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().day_of_week, 1)
