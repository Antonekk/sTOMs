from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from offices.models import Localization, Office
from rest_framework.test import APIClient, APITestCase

from therapist_availability.filters import (
    filter_weekly_availability_blocks,
    get_override_availability_blocks,
    get_weekly_availability_blocks,
)
from therapist_availability.models import AvailabilityBlock, Therapist
from therapist_availability.serializers import (
    BaseScheduleBlockSerializer,
    BaseScheduleSerializer,
    OverrideBlockSerializer,
)
from therapist_availability.services import (
    AvailabilityService,
    ScheduleService,
)
from therapist_availability.utils import exclude_intervals, overlaps

User = get_user_model()


def create_therapist(email="therapist@test.com"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number="+48123456789",
        first_name="Test",
        last_name="Therapist",
        role=User.Role.THERAPIST,
    )
    localization = Localization.objects.create(
        name=f"Lokalizacja {email}",
        city="Warszawa",
        postal_code="00-001",
        address="ul. Testowa 1",
    )
    office = Office.objects.create(localization=localization, room_number="101")
    therapist = Therapist.objects.create(user=user, office=office)
    return user, therapist


class TestOverlapsUtility(TestCase):
    def test_overlaps_partial_overlap(self):
        self.assertTrue(overlaps(time(9, 0), time(10, 30), time(10, 0), time(11, 0)))

    def test_overlaps_adjacent_no_overlap(self):
        self.assertFalse(overlaps(time(9, 0), time(10, 0), time(10, 0), time(11, 0)))


class TestExcludeIntervals(TestCase):
    def test_single_exclusion_splits_block(self):
        availability = [{"start_time": time(9, 0), "end_time": time(17, 0)}]
        exclusions = [{"start_time": time(12, 0), "end_time": time(13, 0)}]
        result = exclude_intervals(availability, exclusions)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["end_time"], time(12, 0))
        self.assertEqual(result[1]["start_time"], time(13, 0))

    def test_exclusion_covers_entire_block(self):
        availability = [{"start_time": time(10, 0), "end_time": time(12, 0)}]
        exclusions = [{"start_time": time(9, 0), "end_time": time(13, 0)}]
        result = exclude_intervals(availability, exclusions)
        self.assertEqual(result, [])


class TestAvailabilityBlockModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist()

    def test_create_valid_base_block(self):
        block = AvailabilityBlock(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        block.full_clean()
        block.save()
        self.assertIsNotNone(block.id)

    def test_base_block_cannot_have_specific_date(self):
        block = AvailabilityBlock(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            specific_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()


class TestAvailabilityService(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("service@test.com")
        cls.monday = date(2025, 6, 2)
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_partial_exclusion_returns_two_intervals(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(12, 0),
            end_time=time(13, 0),
        )
        result = AvailabilityService.get_slots(self.therapist, self.monday)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["end_time"], time(12, 0))
        self.assertEqual(result[1]["start_time"], time(13, 0))

    def test_full_exclusion_returns_empty_list(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        result = AvailabilityService.get_slots(self.therapist, self.monday)
        self.assertEqual(result, [])


class TestScheduleService(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("schedule@test.com")

    def test_replace_base_schedule(self):
        ScheduleService.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 0, "start_time": time(9, 0), "end_time": time(17, 0)},
                {"day_of_week": 2, "start_time": time(10, 0), "end_time": time(16, 0)},
            ],
        )
        self.assertEqual(
            AvailabilityBlock.objects.filter(
                therapist=self.therapist,
                type=AvailabilityBlock.BlockType.BASE,
            ).count(),
            2,
        )

    def test_overlapping_base_blocks_raise(self):
        with self.assertRaises(ValidationError):
            ScheduleService.replace_base_schedule(
                self.therapist,
                [
                    {"day_of_week": 0, "start_time": time(9, 0), "end_time": time(12, 0)},
                    {"day_of_week": 0, "start_time": time(11, 0), "end_time": time(14, 0)},
                ],
            )


class TestFilterFunctions(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("filters@test.com")
        cls.test_date = date(2025, 6, 2)
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=cls.test_date,
            start_time=time(18, 0),
            end_time=time(20, 0),
        )

    def test_get_weekly_availability_blocks(self):
        blocks = get_weekly_availability_blocks(self.therapist, 0)
        self.assertEqual(blocks.count(), 1)

    def test_get_override_availability_blocks(self):
        blocks = get_override_availability_blocks(self.therapist, self.test_date)
        self.assertEqual(blocks.count(), 1)

    def test_filter_weekly_availability_blocks(self):
        blocks = filter_weekly_availability_blocks(
            self.therapist, 0, time(10, 0), time(11, 0)
        )
        self.assertTrue(blocks.exists())


class TestSerializers(TestCase):
    def test_base_schedule_overlapping_blocks_invalid(self):
        serializer = BaseScheduleSerializer(
            data={
                "blocks": [
                    {"day_of_week": 0, "start_time": "09:00", "end_time": "12:00"},
                    {"day_of_week": 0, "start_time": "11:00", "end_time": "14:00"},
                ]
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_override_requires_future_date(self):
        serializer = OverrideBlockSerializer(
            data={
                "type": "EXCLUSION",
                "specific_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "start_time": "10:00",
                "end_time": "11:00",
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_base_block_serializer_valid(self):
        serializer = BaseScheduleBlockSerializer(
            data={"day_of_week": 0, "start_time": "09:00", "end_time": "17:00"}
        )
        self.assertTrue(serializer.is_valid())


class TestSelfScheduleAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist("api-schedule@test.com")
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

    def test_get_returns_base_blocks(self):
        self.client.force_authenticate(user=self.therapist_user)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        response = self.client.get("/api/therapists/self/schedule")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["blocks"]), 1)

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

    def test_put_overlapping_blocks_returns_400(self):
        self.client.force_authenticate(user=self.therapist_user)
        response = self.client.put(
            "/api/therapists/self/schedule",
            {
                "blocks": [
                    {"day_of_week": 0, "start_time": "09:00", "end_time": "12:00"},
                    {"day_of_week": 0, "start_time": "11:00", "end_time": "14:00"},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)


class TestSelfScheduleOverrideAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.therapist_user, cls.therapist = create_therapist("api-override@test.com")
        cls.other_user, cls.other_therapist = create_therapist("other@test.com")
        cls.monday = date(2025, 6, 2)
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
                "specific_date": "2025-06-02",
                "start_time": "10:00",
                "end_time": "12:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

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
