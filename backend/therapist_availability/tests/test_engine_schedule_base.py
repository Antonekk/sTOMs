from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from therapist_availability.engines import ScheduleEngine
from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist


class ScheduleEngineBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("t5@test.com")

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
