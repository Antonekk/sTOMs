from datetime import time, timedelta

from django.test import TestCase
from django.utils import timezone

from therapist_availability.engines import AvailabilityEngine, ScheduleEngine
from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist, next_monday, next_weekday


class ReconcileOverridesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("t8@test.com")
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
        past_friday = timezone.localdate() - timedelta(days=14)
        while past_friday.weekday() != 4:
            past_friday -= timedelta(days=1)
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
