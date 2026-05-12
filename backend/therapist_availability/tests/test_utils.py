from datetime import time

from django.test import TestCase

from therapist_availability.utils import (
    clip_interval_to_blocks,
    exclude_intervals,
    merge_adjacent_blocks,
    merge_overlapping_intervals,
    overlaps,
)


class TestOverlapsUtility(TestCase):
    def test_overlaps_partial_overlap(self):
        self.assertTrue(overlaps(time(9, 0), time(10, 30), time(10, 0), time(11, 0)))

    def test_overlaps_adjacent_no_overlap(self):
        self.assertFalse(overlaps(time(9, 0), time(10, 0), time(10, 0), time(11, 0)))


class TestMergeAdjacentBlocks(TestCase):
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


class TestMergeOverlappingIntervals(TestCase):
    def test_merges_overlapping_intervals(self):
        result = merge_overlapping_intervals(
            [
                {"start_time": time(6, 0), "end_time": time(7, 30)},
                {"start_time": time(7, 0), "end_time": time(8, 0)},
            ]
        )
        self.assertEqual(
            result,
            [{"start_time": time(6, 0), "end_time": time(8, 0)}],
        )

    def test_merges_adjacent_intervals(self):
        result = merge_overlapping_intervals(
            [
                {"start_time": time(10, 0), "end_time": time(11, 0)},
                {"start_time": time(11, 0), "end_time": time(12, 0)},
            ]
        )
        self.assertEqual(
            result,
            [{"start_time": time(10, 0), "end_time": time(12, 0)}],
        )

    def test_keeps_separate_non_overlapping_intervals(self):
        result = merge_overlapping_intervals(
            [
                {"start_time": time(6, 0), "end_time": time(7, 0)},
                {"start_time": time(8, 0), "end_time": time(9, 0)},
            ]
        )
        self.assertEqual(len(result), 2)


class TestClipIntervalToBlocks(TestCase):
    def test_clips_to_single_base_block(self):
        result = clip_interval_to_blocks(
            {"start_time": time(10, 0), "end_time": time(12, 0)},
            [{"start_time": time(9, 0), "end_time": time(11, 0)}],
        )
        self.assertEqual(
            result,
            [{"start_time": time(10, 0), "end_time": time(11, 0)}],
        )

    def test_clips_to_multiple_base_blocks(self):
        result = clip_interval_to_blocks(
            {"start_time": time(10, 0), "end_time": time(14, 0)},
            [
                {"start_time": time(9, 0), "end_time": time(11, 0)},
                {"start_time": time(13, 0), "end_time": time(17, 0)},
            ],
        )
        self.assertEqual(
            result,
            [
                {"start_time": time(10, 0), "end_time": time(11, 0)},
                {"start_time": time(13, 0), "end_time": time(14, 0)},
            ],
        )

    def test_returns_empty_when_no_overlap(self):
        result = clip_interval_to_blocks(
            {"start_time": time(10, 0), "end_time": time(12, 0)},
            [{"start_time": time(13, 0), "end_time": time(17, 0)}],
        )
        self.assertEqual(result, [])
