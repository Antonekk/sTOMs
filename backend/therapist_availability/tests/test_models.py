from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase

from therapist_availability.models import AvailabilityBlock

from .helpers import create_therapist


class AvailabilityBlockModelTestCase(TestCase):
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
