from datetime import date, time
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient

from .engine import (
    exclude_from_availability_blocks,
    generate_daily_availability_blocks,
    merge_to_datetime,
    replace_weekly_schedule,
    validate_exclusion,
    validate_inclusion,
    validate_override,
)
from .filters import (
    filter_weekly_availability_blocks,
    get_override_availability_blocks,
    get_weekly_availability_blocks,
)
from .models import AvailabilityBlock
from .serializers import (
    AvailabilityBlockSerializer,
    TimeRangeBlockSerializer,
    WeeklyScheduleSerializer,
)
from .utils import overlaps


User = get_user_model()


class TestOverlapsUtility(TestCase):
    """Tests for the overlaps utility function."""

    def test_overlaps_completely_separate_before(self):
        """Non-overlapping: first block entirely before second."""
        self.assertFalse(overlaps(
            time(8, 0), time(9, 0),
            time(10, 0), time(11, 0)
        ))

    def test_overlaps_completely_separate_after(self):
        """Non-overlapping: first block entirely after second."""
        self.assertFalse(overlaps(
            time(12, 0), time(13, 0),
            time(10, 0), time(11, 0)
        ))

    def test_overlaps_adjacent_no_overlap(self):
        """Adjacent blocks (touching at edge) should not overlap."""
        self.assertFalse(overlaps(
            time(9, 0), time(10, 0),
            time(10, 0), time(11, 0)
        ))

    def test_overlaps_partial_overlap_start(self):
        """Partial overlap at start."""
        self.assertTrue(overlaps(
            time(9, 0), time(10, 30),
            time(10, 0), time(11, 0)
        ))

    def test_overlaps_partial_overlap_end(self):
        """Partial overlap at end."""
        self.assertTrue(overlaps(
            time(10, 30), time(12, 0),
            time(10, 0), time(11, 0)
        ))

    def test_overlaps_complete_containment(self):
        """First block completely contains second."""
        self.assertTrue(overlaps(
            time(8, 0), time(14, 0),
            time(10, 0), time(12, 0)
        ))

    def test_overlaps_completely_contained(self):
        """First block completely contained in second."""
        self.assertTrue(overlaps(
            time(10, 0), time(11, 0),
            time(9, 0), time(12, 0)
        ))

    def test_overlaps_identical_ranges(self):
        """Identical time ranges should overlap."""
        self.assertTrue(overlaps(
            time(10, 0), time(11, 0),
            time(10, 0), time(11, 0)
        ))


class TestAvailabilityBlockModel(TestCase):
    """Tests for the AvailabilityBlock model validation."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )

    def test_create_valid_weekly_block(self):
        """Valid WEEKLY block with day_of_week should save successfully."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        block.full_clean()
        block.save()
        self.assertIsNotNone(block.id)

    def test_weekly_block_requires_day_of_week(self):
        """WEEKLY block without day_of_week should raise ValidationError."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=None,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_weekly_block_invalid_day_of_week_negative(self):
        """WEEKLY block with negative day_of_week should raise ValidationError."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=-1,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_weekly_block_invalid_day_of_week_too_large(self):
        """WEEKLY block with day_of_week > 6 should raise ValidationError."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=7,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_weekly_block_cannot_have_specific_date(self):
        """WEEKLY block with specific_date should raise ValidationError."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            specific_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_create_valid_inclusion_block(self):
        """Valid INCLUSION block with specific_date should save successfully."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        block.full_clean()
        block.save()
        self.assertIsNotNone(block.id)

    def test_create_valid_exclusion_block(self):
        """Valid EXCLUSION block with specific_date should save successfully."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=date.today(),
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        block.full_clean()
        block.save()
        self.assertIsNotNone(block.id)

    def test_override_block_requires_specific_date(self):
        """INCLUSION/EXCLUSION block without specific_date should raise ValidationError."""
        for block_type in [
            AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
        ]:
            block = AvailabilityBlock(
                therapist=self.therapist,
                availability_type=block_type,
                specific_date=None,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
            with self.assertRaises(ValidationError):
                block.full_clean()

    def test_override_block_cannot_have_day_of_week(self):
        """INCLUSION/EXCLUSION block with day_of_week should raise ValidationError."""
        for block_type in [
            AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
        ]:
            block = AvailabilityBlock(
                therapist=self.therapist,
                availability_type=block_type,
                specific_date=date.today(),
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
            with self.assertRaises(ValidationError):
                block.full_clean()

    def test_start_time_must_be_before_end_time(self):
        """Block with start_time >= end_time should raise ValidationError."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(17, 0),
            end_time=time(9, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_equal_start_and_end_time_invalid(self):
        """Block with equal start_time and end_time should raise ValidationError."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(9, 0),
        )
        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_all_valid_days_of_week(self):
        """All days 0-6 should be valid for WEEKLY blocks."""
        for day in range(7):
            block = AvailabilityBlock(
                therapist=self.therapist,
                availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
            block.full_clean()  # Should not raise


class TestFilterFunctions(TestCase):
    """Tests for scheduling filter functions."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )
        cls.other_therapist = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
            phone_number="+48987654321",
            first_name="Other",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )

        # Create WEEKLY blocks for therapist
        cls.monday_morning = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        cls.monday_afternoon = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(14, 0),
            end_time=time(17, 0),
        )
        cls.tuesday_block = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=1,  # Tuesday
            start_time=time(10, 0),
            end_time=time(16, 0),
        )

        # Create override blocks
        cls.test_date = date(2025, 6, 2)  # A Monday
        cls.inclusion_block = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=cls.test_date,
            start_time=time(18, 0),
            end_time=time(20, 0),
        )
        cls.exclusion_block = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=cls.test_date,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

    def test_get_weekly_availability_blocks_returns_correct_day(self):
        """Should return only blocks for the specified day."""
        blocks = get_weekly_availability_blocks(self.therapist, 0)  # Monday
        self.assertEqual(blocks.count(), 2)
        self.assertIn(self.monday_morning, blocks)
        self.assertIn(self.monday_afternoon, blocks)

    def test_get_weekly_availability_blocks_different_day(self):
        """Should return blocks for different day."""
        blocks = get_weekly_availability_blocks(self.therapist, 1)  # Tuesday
        self.assertEqual(blocks.count(), 1)
        self.assertIn(self.tuesday_block, blocks)

    def test_get_weekly_availability_blocks_empty_day(self):
        """Should return empty queryset for day with no blocks."""
        blocks = get_weekly_availability_blocks(self.therapist, 6)  # Sunday
        self.assertEqual(blocks.count(), 0)

    def test_get_weekly_availability_blocks_only_returns_therapist_blocks(self):
        """Should only return blocks for the specified therapist."""
        # Create block for other therapist
        AvailabilityBlock.objects.create(
            therapist=self.other_therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        blocks = get_weekly_availability_blocks(self.therapist, 0)
        self.assertEqual(blocks.count(), 2)  # Only our therapist's blocks

    def test_get_weekly_availability_blocks_ordered_by_start_time(self):
        """Blocks should be ordered by start_time."""
        blocks = list(get_weekly_availability_blocks(self.therapist, 0))
        self.assertEqual(blocks[0], self.monday_morning)
        self.assertEqual(blocks[1], self.monday_afternoon)

    def test_filter_weekly_availability_blocks_overlapping(self):
        """Should return blocks overlapping with specified time range."""
        blocks = filter_weekly_availability_blocks(
            self.therapist, 0, time(11, 0), time(15, 0)
        )
        self.assertEqual(blocks.count(), 2)

    def test_filter_weekly_availability_blocks_non_overlapping(self):
        """Should return empty queryset when no blocks overlap."""
        blocks = filter_weekly_availability_blocks(
            self.therapist, 0, time(12, 30), time(13, 30)
        )
        self.assertEqual(blocks.count(), 0)

    def test_filter_weekly_availability_blocks_single_overlap(self):
        """Should return only overlapping blocks."""
        blocks = filter_weekly_availability_blocks(
            self.therapist, 0, time(8, 0), time(10, 0)
        )
        self.assertEqual(blocks.count(), 1)
        self.assertIn(self.monday_morning, blocks)

    def test_get_override_availability_blocks_returns_both_types(self):
        """Should return both INCLUSION and EXCLUSION blocks for date."""
        blocks = get_override_availability_blocks(self.therapist, self.test_date)
        self.assertEqual(blocks.count(), 2)
        self.assertIn(self.inclusion_block, blocks)
        self.assertIn(self.exclusion_block, blocks)

    def test_get_override_availability_blocks_different_date(self):
        """Should return empty queryset for date with no overrides."""
        other_date = date(2025, 6, 3)
        blocks = get_override_availability_blocks(self.therapist, other_date)
        self.assertEqual(blocks.count(), 0)

    def test_get_override_availability_blocks_excludes_weekly(self):
        """Should not return WEEKLY blocks."""
        # The WEEKLY blocks exist but shouldn't appear
        blocks = get_override_availability_blocks(self.therapist, self.test_date)
        for block in blocks:
            self.assertNotEqual(
                block.availability_type,
                AvailabilityBlock.AvailabilityBlockType.WEEKLY
            )


class TestExcludeFromAvailabilityBlocks(TestCase):
    """Tests for the exclude_from_availability_blocks engine function."""

    def test_no_exclusions(self):
        """With no exclusions, availability should remain unchanged."""
        availability = [
            {"start_time": time(9, 0), "end_time": time(12, 0)},
            {"start_time": time(14, 0), "end_time": time(17, 0)},
        ]
        result = exclude_from_availability_blocks(availability, [])
        self.assertEqual(result, availability)

    def test_no_availability(self):
        """With no availability, result should be empty."""
        exclusions = [{"start_time": time(10, 0), "end_time": time(11, 0)}]
        result = exclude_from_availability_blocks([], exclusions)
        self.assertEqual(result, [])

    def test_single_exclusion_splits_block(self):
        """Exclusion in middle of block should split it."""
        availability = [{"start_time": time(9, 0), "end_time": time(17, 0)}]
        exclusions = [{"start_time": time(12, 0), "end_time": time(13, 0)}]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"start_time": time(9, 0), "end_time": time(12, 0)})
        self.assertEqual(result[1], {"start_time": time(13, 0), "end_time": time(17, 0)})

    def test_exclusion_at_start(self):
        """Exclusion at start of block should trim beginning."""
        availability = [{"start_time": time(9, 0), "end_time": time(17, 0)}]
        exclusions = [{"start_time": time(9, 0), "end_time": time(11, 0)}]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"start_time": time(11, 0), "end_time": time(17, 0)})

    def test_exclusion_at_end(self):
        """Exclusion at end of block should trim end."""
        availability = [{"start_time": time(9, 0), "end_time": time(17, 0)}]
        exclusions = [{"start_time": time(15, 0), "end_time": time(17, 0)}]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"start_time": time(9, 0), "end_time": time(15, 0)})

    def test_exclusion_covers_entire_block(self):
        """Exclusion covering entire block should remove it."""
        availability = [{"start_time": time(10, 0), "end_time": time(12, 0)}]
        exclusions = [{"start_time": time(9, 0), "end_time": time(13, 0)}]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(len(result), 0)

    def test_multiple_exclusions(self):
        """Multiple exclusions should create multiple splits."""
        availability = [{"start_time": time(9, 0), "end_time": time(17, 0)}]
        exclusions = [
            {"start_time": time(10, 0), "end_time": time(11, 0)},
            {"start_time": time(14, 0), "end_time": time(15, 0)},
        ]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {"start_time": time(9, 0), "end_time": time(10, 0)})
        self.assertEqual(result[1], {"start_time": time(11, 0), "end_time": time(14, 0)})
        self.assertEqual(result[2], {"start_time": time(15, 0), "end_time": time(17, 0)})

    def test_non_overlapping_exclusion(self):
        """Exclusion not overlapping availability should have no effect."""
        availability = [{"start_time": time(9, 0), "end_time": time(12, 0)}]
        exclusions = [{"start_time": time(14, 0), "end_time": time(15, 0)}]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(result, availability)

    def test_multiple_availability_blocks(self):
        """Should handle multiple availability blocks correctly."""
        availability = [
            {"start_time": time(9, 0), "end_time": time(12, 0)},
            {"start_time": time(14, 0), "end_time": time(17, 0)},
        ]
        exclusions = [
            {"start_time": time(10, 0), "end_time": time(11, 0)},
            {"start_time": time(15, 0), "end_time": time(16, 0)},
        ]
        result = exclude_from_availability_blocks(availability, exclusions)
        self.assertEqual(len(result), 4)


class TestMergeToDatetime(TestCase):
    """Tests for the merge_to_datetime helper function."""

    def test_merge_basic(self):
        """Should correctly combine date and time."""
        test_date = date(2025, 6, 15)
        test_time = time(14, 30, 45)
        result = merge_to_datetime(test_date, test_time)
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 45)

    def test_merge_midnight(self):
        """Should handle midnight correctly."""
        test_date = date(2025, 1, 1)
        test_time = time(0, 0, 0)
        result = merge_to_datetime(test_date, test_time)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)


class TestReplaceWeeklySchedule(TestCase):
    """Tests for the replace_weekly_schedule engine function."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )

    def test_creates_new_blocks(self):
        """Should create new weekly blocks."""
        schedule = [
            {"day_of_week": 0, "start_time": time(9, 0), "end_time": time(17, 0)},
            {"day_of_week": 1, "start_time": time(10, 0), "end_time": time(16, 0)},
        ]
        result = replace_weekly_schedule(self.therapist, schedule)
        self.assertEqual(len(result), 2)

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY
        )
        self.assertEqual(blocks.count(), 2)

    def test_replaces_existing_blocks(self):
        """Should delete existing WEEKLY blocks and create new ones."""
        # Create initial block
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(8, 0),
            end_time=time(12, 0),
        )

        # Replace with new schedule
        new_schedule = [
            {"day_of_week": 2, "start_time": time(9, 0), "end_time": time(15, 0)},
        ]
        replace_weekly_schedule(self.therapist, new_schedule)

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().day_of_week, 2)

    def test_empty_schedule_clears_blocks(self):
        """Empty schedule should clear all WEEKLY blocks."""
        # Create initial block
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

        replace_weekly_schedule(self.therapist, [])

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY
        )
        self.assertEqual(blocks.count(), 0)

    def test_does_not_affect_override_blocks(self):
        """Should not delete INCLUSION or EXCLUSION blocks."""
        # Create override blocks
        inclusion = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=date.today(),
            start_time=time(18, 0),
            end_time=time(20, 0),
        )
        exclusion = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        replace_weekly_schedule(self.therapist, [])

        # Override blocks should still exist
        self.assertTrue(AvailabilityBlock.objects.filter(id=inclusion.id).exists())
        self.assertTrue(AvailabilityBlock.objects.filter(id=exclusion.id).exists())


class TestValidateExclusion(TestCase):
    """Tests for the validate_exclusion engine function."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )
        # Monday = weekday 0
        cls.monday = date(2025, 6, 2)

        # Create weekly block for Monday
        cls.weekly_block = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_valid_exclusion_overlaps_weekly(self):
        """Exclusion overlapping weekly block should be valid."""
        # Should not raise
        validate_exclusion(
            self.therapist,
            self.monday,
            time(10, 0),
            time(12, 0)
        )

    def test_exclusion_must_overlap_weekly_block(self):
        """Exclusion not overlapping any weekly block should raise."""
        with self.assertRaises(ValidationError):
            validate_exclusion(
                self.therapist,
                self.monday,
                time(18, 0),  # Outside weekly block
                time(20, 0)
            )

    def test_exclusion_cannot_overlap_other_exclusion(self):
        """Exclusion overlapping existing exclusion should raise."""
        # Create existing exclusion
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

        with self.assertRaises(ValidationError):
            validate_exclusion(
                self.therapist,
                self.monday,
                time(11, 0),  # Overlaps with existing
                time(13, 0)
            )

    def test_non_overlapping_exclusions_valid(self):
        """Non-overlapping exclusions should be valid."""
        # Create existing exclusion
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        # Should not raise
        validate_exclusion(
            self.therapist,
            self.monday,
            time(14, 0),
            time(15, 0)
        )


class TestValidateInclusion(TestCase):
    """Tests for the validate_inclusion engine function."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )
        cls.monday = date(2025, 6, 2)

        # Create weekly block for Monday 9-17
        cls.weekly_block = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_valid_inclusion_extends_before(self):
        """Inclusion starting before weekly block should be valid."""
        validate_inclusion(
            self.therapist,
            self.monday,
            time(7, 0),  # Before weekly starts
            time(10, 0)
        )

    def test_valid_inclusion_extends_after(self):
        """Inclusion ending after weekly block should be valid."""
        validate_inclusion(
            self.therapist,
            self.monday,
            time(16, 0),
            time(20, 0)  # After weekly ends
        )

    def test_inclusion_must_extend_weekly(self):
        """Inclusion fully within weekly block should raise."""
        with self.assertRaises(ValidationError):
            validate_inclusion(
                self.therapist,
                self.monday,
                time(10, 0),  # Within 9-17
                time(12, 0)
            )

    def test_inclusion_cannot_overlap_other_inclusion(self):
        """Inclusion overlapping existing inclusion should raise."""
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=self.monday,
            start_time=time(18, 0),
            end_time=time(20, 0),
        )

        with self.assertRaises(ValidationError):
            validate_inclusion(
                self.therapist,
                self.monday,
                time(19, 0),  # Overlaps
                time(21, 0)
            )

    def test_inclusion_valid_on_day_without_weekly(self):
        """Inclusion on day without weekly block should be valid."""
        sunday = date(2025, 6, 8)  # No weekly block for Sunday
        validate_inclusion(
            self.therapist,
            sunday,
            time(10, 0),
            time(14, 0)
        )


class TestValidateOverride(TestCase):
    """Tests for the validate_override engine function."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )
        cls.monday = date(2025, 6, 2)

        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_routes_exclusion_to_validate_exclusion(self):
        """Should call validate_exclusion for EXCLUSION type."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        # Should not raise
        validate_override(block)

    def test_routes_inclusion_to_validate_inclusion(self):
        """Should call validate_inclusion for INCLUSION type."""
        block = AvailabilityBlock(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=self.monday,
            start_time=time(7, 0),  # Extends before weekly
            end_time=time(10, 0),
        )
        # Should not raise
        validate_override(block)


class TestGenerateDailyAvailabilityBlocks(TestCase):
    """Tests for the generate_daily_availability_blocks engine function."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )
        cls.monday = date(2025, 6, 2)

        # Create weekly blocks for Monday
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(14, 0),
            end_time=time(17, 0),
        )

    @patch('scheduling.engine.filter_appointments_for_day')
    def test_basic_weekly_schedule(self, mock_appointments):
        """Should return weekly blocks when no overrides or appointments."""
        mock_appointments.return_value = []

        result = generate_daily_availability_blocks(self.therapist, self.monday)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["start_time"], time(9, 0))
        self.assertEqual(result[0]["end_time"], time(12, 0))
        self.assertEqual(result[1]["start_time"], time(14, 0))
        self.assertEqual(result[1]["end_time"], time(17, 0))

    @patch('scheduling.engine.filter_appointments_for_day')
    def test_with_inclusion_block(self, mock_appointments):
        """Should include INCLUSION blocks in availability."""
        mock_appointments.return_value = []

        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=self.monday,
            start_time=time(18, 0),
            end_time=time(20, 0),
        )

        result = generate_daily_availability_blocks(self.therapist, self.monday)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[2]["start_time"], time(18, 0))
        self.assertEqual(result[2]["end_time"], time(20, 0))

    @patch('scheduling.engine.filter_appointments_for_day')
    def test_with_exclusion_block(self, mock_appointments):
        """Should remove time from availability for EXCLUSION blocks."""
        mock_appointments.return_value = []

        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(11, 0),
        )

        result = generate_daily_availability_blocks(self.therapist, self.monday)

        # Morning block should be split: 9-10 and 11-12
        self.assertEqual(result[0]["start_time"], time(9, 0))
        self.assertEqual(result[0]["end_time"], time(10, 0))
        self.assertEqual(result[1]["start_time"], time(11, 0))
        self.assertEqual(result[1]["end_time"], time(12, 0))

    @patch('scheduling.engine.filter_appointments_for_day')
    def test_with_appointment(self, mock_appointments):
        """Should exclude appointment times from availability."""
        # Mock an appointment
        mock_appointment = MagicMock()
        mock_appointment.appointment_series.start_time = time(15, 0)
        mock_appointment.appointment_series.end_time = time(16, 0)
        mock_appointments.return_value = [mock_appointment]

        result = generate_daily_availability_blocks(self.therapist, self.monday)

        # Afternoon block should be split: 14-15 and 16-17
        afternoon_blocks = [b for b in result if b["start_time"] >= time(14, 0)]
        self.assertEqual(len(afternoon_blocks), 2)
        self.assertEqual(afternoon_blocks[0]["end_time"], time(15, 0))
        self.assertEqual(afternoon_blocks[1]["start_time"], time(16, 0))

    @patch('scheduling.engine.filter_appointments_for_day')
    def test_empty_day(self, mock_appointments):
        """Day with no weekly blocks should return empty."""
        mock_appointments.return_value = []

        sunday = date(2025, 6, 8)  # No weekly blocks
        result = generate_daily_availability_blocks(self.therapist, sunday)

        self.assertEqual(len(result), 0)


class TestTimeRangeBlockSerializer(TestCase):
    """Tests for TimeRangeBlockSerializer."""

    def test_valid_time_range(self):
        """Valid time range should pass validation."""
        data = {"start_time": "09:00", "end_time": "17:00"}
        serializer = TimeRangeBlockSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_time_range_start_after_end(self):
        """start_time >= end_time should fail validation."""
        data = {"start_time": "17:00", "end_time": "09:00"}
        serializer = TimeRangeBlockSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_equal_times_invalid(self):
        """Equal start and end times should fail validation."""
        data = {"start_time": "09:00", "end_time": "09:00"}
        serializer = TimeRangeBlockSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_missing_fields(self):
        """Missing required fields should fail validation."""
        serializer = TimeRangeBlockSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("start_time", serializer.errors)
        self.assertIn("end_time", serializer.errors)


class TestWeeklyScheduleSerializer(TestCase):
    """Tests for WeeklyScheduleSerializer."""

    def test_valid_schedule(self):
        """Valid weekly schedule should pass validation."""
        data = {
            "weekly_schedule": {
                "0": [{"start_time": "09:00", "end_time": "12:00"}],
                "1": [{"start_time": "10:00", "end_time": "16:00"}],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_day_of_week_string(self):
        """Non-numeric day of week should fail validation."""
        data = {
            "weekly_schedule": {
                "monday": [{"start_time": "09:00", "end_time": "12:00"}],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_day_of_week_negative(self):
        """Negative day of week should fail validation."""
        data = {
            "weekly_schedule": {
                "-1": [{"start_time": "09:00", "end_time": "12:00"}],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_day_of_week_too_large(self):
        """Day of week > 6 should fail validation."""
        data = {
            "weekly_schedule": {
                "7": [{"start_time": "09:00", "end_time": "12:00"}],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_overlapping_blocks_invalid(self):
        """Overlapping blocks on same day should fail validation."""
        data = {
            "weekly_schedule": {
                "0": [
                    {"start_time": "09:00", "end_time": "12:00"},
                    {"start_time": "11:00", "end_time": "14:00"},  # Overlaps
                ],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_adjacent_blocks_valid(self):
        """Adjacent (touching) blocks should be valid."""
        data = {
            "weekly_schedule": {
                "0": [
                    {"start_time": "09:00", "end_time": "12:00"},
                    {"start_time": "12:00", "end_time": "15:00"},
                ],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_empty_schedule_valid(self):
        """Empty schedule should be valid."""
        data = {"weekly_schedule": {}}
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_blocks_sorted_by_start_time(self):
        """Validated blocks should be sorted by start_time."""
        data = {
            "weekly_schedule": {
                "0": [
                    {"start_time": "14:00", "end_time": "17:00"},
                    {"start_time": "09:00", "end_time": "12:00"},
                ],
            }
        }
        serializer = WeeklyScheduleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        blocks = serializer.validated_data["weekly_schedule"][0]
        self.assertEqual(blocks[0]["start_time"], time(9, 0))
        self.assertEqual(blocks[1]["start_time"], time(14, 0))


class TestAvailabilityBlockSerializer(TestCase):
    """Tests for AvailabilityBlockSerializer."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )

    def test_valid_inclusion_data(self):
        """Valid INCLUSION block data should pass validation."""
        data = {
            "specific_date": "2025-06-02",
            "start_time": "18:00",
            "end_time": "20:00",
            "availability_type": "INCLUSION",
        }
        serializer = AvailabilityBlockSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_valid_exclusion_data(self):
        """Valid EXCLUSION block data should pass validation."""
        data = {
            "specific_date": "2025-06-02",
            "start_time": "10:00",
            "end_time": "11:00",
            "availability_type": "EXCLUSION",
        }
        serializer = AvailabilityBlockSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_read_only_fields(self):
        """id and therapist should be read-only."""
        data = {
            "id": "12345678-1234-1234-1234-123456789012",
            "therapist": str(self.therapist.id),
            "specific_date": "2025-06-02",
            "start_time": "10:00",
            "end_time": "11:00",
            "availability_type": "EXCLUSION",
        }
        serializer = AvailabilityBlockSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # id and therapist should not be in validated_data
        self.assertNotIn("id", serializer.validated_data)
        self.assertNotIn("therapist", serializer.validated_data)

    def test_serializes_existing_block(self):
        """Should correctly serialize existing block."""
        block = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=date(2025, 6, 2),
            start_time=time(18, 0),
            end_time=time(20, 0),
        )
        serializer = AvailabilityBlockSerializer(block)
        self.assertEqual(serializer.data["specific_date"], "2025-06-02")
        self.assertEqual(serializer.data["availability_type"], "INCLUSION")


class TestTherapistScheduleViewAPI(APITestCase):
    """API tests for TherapistScheduleView."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
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

    def test_list_requires_authentication(self):
        """GET /schedule/ should require authentication."""
        response = self.client.get("/api/schedule/")
        self.assertEqual(response.status_code, 401)

    def test_list_requires_therapist_role(self):
        """GET /schedule/ should require therapist role."""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get("/api/schedule/")
        self.assertEqual(response.status_code, 403)

    def test_list_returns_weekly_schedule(self):
        """GET /schedule/ should return therapist's weekly schedule."""
        self.client.force_authenticate(user=self.therapist)

        # Create blocks
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

        response = self.client.get("/api/schedule/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(0, response.data)
        self.assertEqual(len(response.data[0]), 1)

    def test_create_weekly_schedule(self):
        """POST /schedule/ should create weekly schedule."""
        self.client.force_authenticate(user=self.therapist)

        data = {
            "weekly_schedule": {
                "0": [{"start_time": "09:00", "end_time": "17:00"}],
                "2": [{"start_time": "10:00", "end_time": "16:00"}],
            }
        }

        response = self.client.post("/api/schedule/", data, format="json")
        self.assertEqual(response.status_code, 201)

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY
        )
        self.assertEqual(blocks.count(), 2)

    def test_create_replaces_existing_schedule(self):
        """POST /schedule/ should replace existing weekly blocks."""
        self.client.force_authenticate(user=self.therapist)

        # Create initial block
        AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(8, 0),
            end_time=time(12, 0),
        )

        # Replace with new schedule
        data = {
            "weekly_schedule": {
                "1": [{"start_time": "09:00", "end_time": "17:00"}],
            }
        }

        response = self.client.post("/api/schedule/", data, format="json")
        self.assertEqual(response.status_code, 201)

        blocks = AvailabilityBlock.objects.filter(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY
        )
        self.assertEqual(blocks.count(), 1)
        self.assertEqual(blocks.first().day_of_week, 1)


class TestTherapistScheduleOverrideAPI(APITestCase):
    """API tests for TherapistScheduleOverride."""

    @classmethod
    def setUpTestData(cls):
        cls.therapist = User.objects.create_user(
            email="therapist@test.com",
            password="testpass123",
            phone_number="+48123456789",
            first_name="Test",
            last_name="Therapist",
            role=User.Role.THERAPIST,
        )
        cls.monday = date(2025, 6, 2)

        # Create weekly block
        cls.weekly_block = AvailabilityBlock.objects.create(
            therapist=cls.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.therapist)

    def test_list_override_blocks(self):
        """GET /schedule/override/ should return override blocks."""
        # Create override block
        inclusion = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            specific_date=self.monday,
            start_time=time(18, 0),
            end_time=time(20, 0),
        )

        response = self.client.get("/api/schedule/override/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(inclusion.id))

    def test_list_excludes_weekly_blocks(self):
        """GET /schedule/override/ should not return WEEKLY blocks."""
        response = self.client.get("/api/schedule/override/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_create_valid_exclusion(self):
        """POST /schedule/override/ should create valid exclusion."""
        data = {
            "specific_date": "2025-06-02",
            "start_time": "10:00",
            "end_time": "12:00",
            "availability_type": "EXCLUSION",
        }

        response = self.client.post("/api/schedule/override/", data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_invalid_exclusion_no_overlap(self):
        """POST /schedule/override/ should reject exclusion not overlapping weekly."""
        data = {
            "specific_date": "2025-06-02",
            "start_time": "18:00",  # Outside weekly block
            "end_time": "20:00",
            "availability_type": "EXCLUSION",
        }

        response = self.client.post("/api/schedule/override/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_create_valid_inclusion(self):
        """POST /schedule/override/ should create valid inclusion."""
        data = {
            "specific_date": "2025-06-02",
            "start_time": "17:00",  # Extends after weekly
            "end_time": "20:00",
            "availability_type": "INCLUSION",
        }

        response = self.client.post("/api/schedule/override/", data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_delete_override_block(self):
        """DELETE /schedule/override/{id}/ should delete block."""
        exclusion = AvailabilityBlock.objects.create(
            therapist=self.therapist,
            availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
            specific_date=self.monday,
            start_time=time(10, 0),
            end_time=time(12, 0),
        )

        response = self.client.delete(f"/api/schedule/override/{exclusion.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AvailabilityBlock.objects.filter(id=exclusion.id).exists())
