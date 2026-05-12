from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist, next_monday

User = get_user_model()


class TestSelfScheduleAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist(
            "api-schedule@test.com", "+48123456782"
        )
        cls.client_user = User.objects.create_user(
            email="client@test.com",
            password="testpass123",
            phone_number="+48111222333",
            first_name="Test",
            last_name="Client",
            role=User.Role.CLIENT,
        )

    def setUp(self):
        self.client = APIClient()

    def test_get_requires_therapist_role(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get("/api/therapists/self/schedule")
        self.assertEqual(response.status_code, 403)

    def test_put_replaces_existing_blocks(self):
        self.client.force_authenticate(user=self.therapist_user)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(8, 0),
            end_time=time(12, 0),
        )
        response = self.client.put(
            "/api/therapists/self/schedule",
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


class TestSelfScheduleOverrideAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist(
            "api-override@test.com", "+48123456783"
        )
        cls.other_user, cls.other_therapist = create_therapist(
            "other@test.com", "+48123456784"
        )
        cls.monday = next_monday()
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.therapist_user)

    def test_create_exclusion(self):
        response = self.client.post(
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
        response = self.client.post(
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
        response = self.client.delete(
            f"/api/therapists/self/schedule/override/{exclusion.id}"
        )
        self.assertEqual(response.status_code, 404)
