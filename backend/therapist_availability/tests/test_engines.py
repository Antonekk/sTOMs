from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from therapist_availability.engines import AvailabilityEngine, ScheduleEngine
from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist, next_monday, next_weekday

User = get_user_model()


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

        merged_block = ScheduleEngine.normalize_overrides_for_date(
            self.therapist,
            target_date,
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

        merged_block = ScheduleEngine.normalize_overrides_for_date(
            self.therapist,
            target_date,
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

    def test_overlapping_inclusions_are_merged(self):
        target_date = next_weekday(4)
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
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
            start_time=time(6, 0),
            end_time=time(7, 30),
        )
        second_block = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
            start_time=time(7, 0),
            end_time=time(8, 0),
        )

        ScheduleEngine.normalize_overrides_for_date(
            self.therapist,
            target_date,
            source_block=second_block,
        )

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().start_time, time(6, 0))
        self.assertEqual(blocks.first().end_time, time(8, 0))

    def test_overlapping_exclusions_are_merged(self):
        target_date = next_weekday(0)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
            start_time=time(10, 0),
            end_time=time(11, 30),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

        ScheduleEngine.normalize_overrides_for_date(self.therapist, target_date)

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().start_time, time(10, 0))
        self.assertEqual(blocks.first().end_time, time(12, 0))

    def test_exclusion_shrinks_overlapping_inclusion(self):
        target_date = next_weekday(4)
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
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
            start_time=time(12, 0),
            end_time=time(14, 0),
        )
        exclusion = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
            start_time=time(13, 0),
            end_time=time(15, 0),
        )

        ScheduleEngine.normalize_overrides_for_date(
            self.therapist,
            target_date,
            source_block=exclusion,
        )

        inclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
        )
        exclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
        )
        self.assertEqual(inclusion.start_time, time(12, 0))
        self.assertEqual(inclusion.end_time, time(13, 0))
        self.assertEqual(exclusion.start_time, time(14, 0))
        self.assertEqual(exclusion.end_time, time(15, 0))

    def test_inclusion_shrinks_overlapping_exclusion(self):
        target_date = next_weekday(4)
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
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
            start_time=time(13, 0),
            end_time=time(15, 0),
        )
        inclusion = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
            start_time=time(12, 0),
            end_time=time(14, 0),
        )

        ScheduleEngine.normalize_overrides_for_date(
            self.therapist,
            target_date,
            source_block=inclusion,
        )

        inclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
        )
        exclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
        )
        self.assertEqual(inclusion.start_time, time(12, 0))
        self.assertEqual(inclusion.end_time, time(13, 0))
        self.assertEqual(exclusion.start_time, time(14, 0))
        self.assertEqual(exclusion.end_time, time(15, 0))


class TestReconcileOverridesAfterBaseChange(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist(
            "reconcile@test.com", "+48123456784"
        )
        cls.friday = next_weekday(4)
        cls.monday = next_monday()

    def test_inclusion_absorbed_by_merged_base_is_removed(self):
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
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=self.friday,
            start_time=time(12, 0),
            end_time=time(14, 0),
        )

        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(17, 0)},
            ],
        )

        self.assertFalse(
            AvailabilityBlock.objects.filter(
                therapist=self.therapist,
                type=AvailabilityBlock.BlockType.INCLUSION,
                specific_date=self.friday,
            ).exists()
        )

    def test_inclusion_partially_overlapping_base_is_trimmed(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=self.friday,
            start_time=time(7, 0),
            end_time=time(9, 0),
        )

        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(17, 0)},
            ],
        )

        inclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=self.friday,
        )
        self.assertEqual(inclusion.start_time, time(7, 0))
        self.assertEqual(inclusion.end_time, time(8, 0))

    def test_exclusion_without_base_on_that_weekday_is_removed(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(17, 0)},
            ],
        )

        self.assertFalse(
            AvailabilityBlock.objects.filter(
                therapist=self.therapist,
                type=AvailabilityBlock.BlockType.EXCLUSION,
                specific_date=self.monday,
            ).exists()
        )

    def test_exclusion_is_trimmed_to_new_base(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.friday,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 4, "start_time": time(9, 0), "end_time": time(11, 0)},
            ],
        )

        exclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=self.friday,
        )
        self.assertEqual(exclusion.start_time, time(10, 0))
        self.assertEqual(exclusion.end_time, time(11, 0))

    def test_past_overrides_are_not_reconciled(self):
        past_friday = self.friday - timedelta(days=7)
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=past_friday,
            start_time=time(7, 0),
            end_time=time(9, 0),
        )

        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 4, "start_time": time(8, 0), "end_time": time(17, 0)},
            ],
        )

        inclusion = AvailabilityBlock.objects.get(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=past_friday,
        )
        self.assertEqual(inclusion.start_time, time(7, 0))
        self.assertEqual(inclusion.end_time, time(9, 0))

    def test_reconcile_eliminates_duplicate_slots_from_absorbed_inclusion(self):
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=4,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=self.friday,
            start_time=time(7, 0),
            end_time=time(9, 0),
        )

        ScheduleEngine.replace_base_schedule(
            self.therapist,
            [
                {"day_of_week": 4, "start_time": time(7, 0), "end_time": time(17, 0)},
            ],
        )

        slots = AvailabilityEngine.get_slots(self.therapist, self.friday)
        self.assertEqual(
            slots,
            [{"start_time": time(7, 0), "end_time": time(17, 0)}],
        )
