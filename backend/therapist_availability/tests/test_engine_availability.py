from datetime import date, time

from django.test import TestCase

from therapist_availability.engines import AvailabilityEngine
from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist


class AvailabilityEngineTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _, cls.therapist = create_therapist("t4@test.com")
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
