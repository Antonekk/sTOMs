from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from offices.models import Localization, Office
from rest_framework.test import APIClient, APITestCase

from therapist_availability.models import AvailabilityBlock, Therapist
from therapist_availability.serializers import (
    BaseScheduleBlockSerializer,
    BaseScheduleSerializer,
    OverrideBlockSerializer,
)
from therapist_availability.engines import (
    AvailabilityEngine,
    ScheduleEngine,
)
from therapist_availability.utils import exclude_intervals, merge_adjacent_blocks, merge_adjacent_date_blocks, overlaps

User = get_user_model()


def next_monday(from_date=None):
    from_date = from_date or timezone.localdate()
    days_ahead = (7 - from_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return from_date + timedelta(days=days_ahead)


def create_therapist(email="therapist@test.com", phone_number="+48123456789"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number=phone_number,
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


class TestMergeAdjacentBlocks(TestCase):
    def test_merges_touching_blocks_on_same_day(self):
        blocks = [
            {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(9, 0)},
            {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(17, 0)},
        ]
        result = merge_adjacent_blocks(blocks)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start_time"], time(8, 0))
        self.assertEqual(result[0]["end_time"], time(17, 0))

    def test_merges_chain_of_adjacent_blocks(self):
        blocks = [
            {"day_of_week": 0, "start_time": time(8, 0), "end_time": time(10, 0)},
            {"day_of_week": 0, "start_time": time(10, 0), "end_time": time(12, 0)},
            {"day_of_week": 0, "start_time": time(12, 0), "end_time": time(14, 0)},
        ]
        result = merge_adjacent_blocks(blocks)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start_time"], time(8, 0))
        self.assertEqual(result[0]["end_time"], time(14, 0))

    def test_keeps_separate_blocks_with_gap(self):
        blocks = [
            {"day_of_week": 0, "start_time": time(8, 0), "end_time": time(10, 0)},
            {"day_of_week": 0, "start_time": time(11, 0), "end_time": time(14, 0)},
        ]
        result = merge_adjacent_blocks(blocks)
        self.assertEqual(len(result), 2)

    def test_merges_per_day_independently(self):
        blocks = [
            {"day_of_week": 0, "start_time": time(9, 0), "end_time": time(12, 0)},
            {"day_of_week": 0, "start_time": time(12, 0), "end_time": time(15, 0)},
            {"day_of_week": 1, "start_time": time(10, 0), "end_time": time(12, 0)},
            {"day_of_week": 1, "start_time": time(12, 0), "end_time": time(16, 0)},
        ]
        result = merge_adjacent_blocks(blocks)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["day_of_week"], 0)
        self.assertEqual(result[1]["day_of_week"], 1)


class TestMergeAdjacentDateBlocks(TestCase):
    def test_merges_touching_inclusions_on_same_date(self):
        target_date = date(2026, 6, 5)
        blocks = [
            {
                "specific_date": target_date,
                "start_time": time(6, 0),
                "end_time": time(7, 0),
            },
            {
                "specific_date": target_date,
                "start_time": time(7, 0),
                "end_time": time(8, 0),
            },
        ]
        result = merge_adjacent_date_blocks(blocks)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["start_time"], time(6, 0))
        self.assertEqual(result[0]["end_time"], time(8, 0))

    def test_keeps_separate_inclusions_with_gap(self):
        target_date = date(2026, 6, 5)
        blocks = [
            {
                "specific_date": target_date,
                "start_time": time(6, 0),
                "end_time": time(7, 0),
            },
            {
                "specific_date": target_date,
                "start_time": time(8, 0),
                "end_time": time(9, 0),
            },
        ]
        result = merge_adjacent_date_blocks(blocks)
        self.assertEqual(len(result), 2)


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


class TestAvailabilityEngine(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("service@test.com", "+48123456780")
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
        result = AvailabilityEngine.get_slots(self.therapist, self.monday)
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
        result = AvailabilityEngine.get_slots(self.therapist, self.monday)
        self.assertEqual(result, [])


class TestScheduleEngine(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("schedule@test.com", "+48123456781")

    def test_replace_base_schedule(self):
        ScheduleEngine.replace_base_schedule(
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
            ScheduleEngine.replace_base_schedule(
                self.therapist,
                [
                    {"day_of_week": 0, "start_time": time(9, 0), "end_time": time(12, 0)},
                    {"day_of_week": 0, "start_time": time(11, 0), "end_time": time(14, 0)},
                ],
            )

    def test_inclusion_overlapping_base_schedule_raises(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            ScheduleEngine.validate_inclusion(
                self.therapist,
                date(2026, 6, 5),
                time(8, 0),
                time(16, 0),
            )

    def test_inclusion_extending_before_base_schedule_is_allowed(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        ScheduleEngine.validate_inclusion(
            self.therapist,
            date(2026, 6, 5),
            time(7, 0),
            time(9, 0),
        )

    def test_inclusion_filling_gap_between_base_blocks_is_allowed(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(14, 0),
            end_time=time(17, 0),
        )
        ScheduleEngine.validate_inclusion(
            self.therapist,
            date(2026, 6, 5),
            time(12, 0),
            time(14, 0),
        )

    def test_adjacent_base_blocks_are_merged_on_save(self):
        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(9, 0)},
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(17, 0)},
            ],
        )
        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
        )
        self.assertEqual(blocks.count(), 1)
        block = blocks.first()
        self.assertEqual(block.start_time, time(8, 0))
        self.assertEqual(block.end_time, time(17, 0))

    def test_adjacent_inclusions_are_merged_on_save(self):
        target_date = date(2026, 6, 5)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
            start_time=time(6, 0),
            end_time=time(7, 0),
        )
        second_block = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
            start_time=time(7, 0),
            end_time=time(8, 0),
        )

        merged_block = ScheduleEngine.merge_adjacent_overrides(
            self.therapist,
            target_date,
            AvailabilityBlock.BlockType.INCLUSION,
            source_block=second_block,
        )

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(merged_block.start_time, time(6, 0))
        self.assertEqual(merged_block.end_time, time(8, 0))

    def test_adjacent_exclusions_are_merged_on_save(self):
        target_date = date(2026, 6, 2)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=target_date.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )
        second_block = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

        merged_block = ScheduleEngine.merge_adjacent_overrides(
            self.therapist,
            target_date,
            AvailabilityBlock.BlockType.EXCLUSION,
            source_block=second_block,
        )

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(merged_block.start_time, time(10, 0))
        self.assertEqual(merged_block.end_time, time(12, 0))


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

    def test_get_merges_adjacent_base_blocks(self):
        self.client.force_authenticate(user=self.therapist_user)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        response = self.client.get("/api/therapists/self/schedule")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["blocks"]), 1)
        self.assertEqual(response.data["blocks"][0]["start_time"], "08:00:00")
        self.assertEqual(response.data["blocks"][0]["end_time"], "17:00:00")

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

    def test_create_inclusion_overlapping_base_schedule_returns_400(self):
        response = self.client.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "INCLUSION",
                "specific_date": self.monday.isoformat(),
                "start_time": "08:00",
                "end_time": "16:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_adjacent_inclusions_are_merged(self):
        response = self.client.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "INCLUSION",
                "specific_date": self.monday.isoformat(),
                "start_time": "06:00",
                "end_time": "07:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "INCLUSION",
                "specific_date": self.monday.isoformat(),
                "start_time": "07:00",
                "end_time": "08:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["start_time"], "06:00:00")
        self.assertEqual(response.data["end_time"], "08:00:00")

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=self.monday,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().start_time, time(6, 0))
        self.assertEqual(blocks.first().end_time, time(8, 0))

    def test_create_adjacent_exclusions_are_merged(self):
        response = self.client.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "EXCLUSION",
                "specific_date": self.monday.isoformat(),
                "start_time": "10:00",
                "end_time": "11:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/api/therapists/self/schedule/override",
            {
                "type": "EXCLUSION",
                "specific_date": self.monday.isoformat(),
                "start_time": "11:00",
                "end_time": "12:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["start_time"], "10:00:00")
        self.assertEqual(response.data["end_time"], "12:00:00")

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.monday,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().start_time, time(10, 0))
        self.assertEqual(blocks.first().end_time, time(12, 0))

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
