from datetime import date, time

from django.test import TestCase

from therapist_availability.engines import ScheduleEngine
from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist, next_weekday


class ScheduleEngineOverrideMergeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("t6@test.com")

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


class ScheduleEngineCrossOverrideTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("t7@test.com")

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
