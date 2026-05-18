from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from therapist_availability.models import AvailabilityBlock
from therapist_availability.utils import (
    clip_interval_to_blocks,
    exclude_intervals,
    has_overlapping_intervals,
    merge_adjacent_blocks,
    merge_overlapping_intervals,
    overlaps,
)


class ScheduleEngine:
    @staticmethod
    def validate_base_blocks_overlap(blocks):
        by_day = {}
        for block in blocks:
            by_day.setdefault(block["day_of_week"], []).append(block)

        for day_blocks in by_day.values():
            if has_overlapping_intervals(day_blocks):
                raise ValidationError(
                    _("Nakładające się bloki w tym samym dniu tygodnia")
                )

    @classmethod
    @transaction.atomic
    def replace_base_schedule(cls, therapist, blocks):
        cls.validate_base_blocks_overlap(blocks)
        merged_blocks = merge_adjacent_blocks(blocks)

        AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.BASE,
        ).delete()

        AvailabilityBlock.objects.bulk_create(
            [
                AvailabilityBlock(
                    therapist=therapist,
                    type=AvailabilityBlock.BlockType.BASE,
                    day_of_week=block["day_of_week"],
                    start_time=block["start_time"],
                    end_time=block["end_time"],
                )
                for block in merged_blocks
            ]
        )
        cls.reconcile_overrides_after_base_change(therapist)

    @classmethod
    def reconcile_overrides_after_base_change(cls, therapist):
        today = timezone.localdate()
        override_dates = (
            AvailabilityBlock.objects.filter(
                therapist=therapist,
                type__in=[
                    AvailabilityBlock.BlockType.INCLUSION,
                    AvailabilityBlock.BlockType.EXCLUSION,
                ],
                specific_date__gte=today,
            )
            .values_list("specific_date", flat=True)
            .distinct()
        )

        for target_date in override_dates:
            cls.normalize_overrides_for_date(therapist, target_date)

    @staticmethod
    def _weekly_base_blocks_queryset(therapist, target_date):
        return AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=target_date.weekday(),
        )

    @staticmethod
    def _base_blocks_for_date(therapist, target_date):
        return [
            {"start_time": block.start_time, "end_time": block.end_time}
            for block in ScheduleEngine._weekly_base_blocks_queryset(
                therapist, target_date
            ).order_by("start_time")
        ]

    @classmethod
    def _raw_intervals_for_type(cls, therapist, target_date, block_type):
        return [
            {"start_time": block.start_time, "end_time": block.end_time}
            for block in AvailabilityBlock.objects.filter(
                therapist=therapist,
                type=block_type,
                specific_date=target_date,
            ).order_by("start_time")
        ]

    @classmethod
    def _apply_base_constraints(cls, intervals, block_type, base_blocks):
        result = []
        for interval in intervals:
            if block_type == AvailabilityBlock.BlockType.INCLUSION:
                result.extend(exclude_intervals([interval], base_blocks))
            else:
                result.extend(clip_interval_to_blocks(interval, base_blocks))
        return merge_overlapping_intervals(result)

    @staticmethod
    def _subtract_intervals(intervals, subtrahend):
        return merge_overlapping_intervals(
            part
            for interval in intervals
            for part in exclude_intervals([interval], subtrahend)
        )

    @classmethod
    def _resolve_cross_type_overrides(cls, inclusions, exclusions):
        return (
            cls._subtract_intervals(inclusions, exclusions),
            cls._subtract_intervals(exclusions, inclusions),
        )

    @classmethod
    def _save_intervals_if_changed(cls, therapist, target_date, block_type, intervals):
        blocks = list(
            AvailabilityBlock.objects.filter(
                therapist=therapist,
                type=block_type,
                specific_date=target_date,
            ).order_by("start_time")
        )
        old_intervals = [
            {"start_time": block.start_time, "end_time": block.end_time}
            for block in blocks
        ]
        if old_intervals == intervals:
            return

        AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=block_type,
            specific_date=target_date,
        ).delete()

        if not intervals:
            return

        AvailabilityBlock.objects.bulk_create(
            [
                AvailabilityBlock(
                    therapist=therapist,
                    type=block_type,
                    specific_date=target_date,
                    start_time=interval["start_time"],
                    end_time=interval["end_time"],
                )
                for interval in intervals
            ]
        )

    @classmethod
    @transaction.atomic
    def normalize_overrides_for_date(cls, therapist, target_date, source_block=None):
        base_blocks = cls._base_blocks_for_date(therapist, target_date)
        raw_inclusions = cls._raw_intervals_for_type(
            therapist,
            target_date,
            AvailabilityBlock.BlockType.INCLUSION,
        )
        raw_exclusions = cls._raw_intervals_for_type(
            therapist,
            target_date,
            AvailabilityBlock.BlockType.EXCLUSION,
        )
        inclusions, exclusions = cls._resolve_cross_type_overrides(
            raw_inclusions,
            raw_exclusions,
        )
        inclusions = cls._apply_base_constraints(
            inclusions,
            AvailabilityBlock.BlockType.INCLUSION,
            base_blocks,
        )
        exclusions = cls._apply_base_constraints(
            exclusions,
            AvailabilityBlock.BlockType.EXCLUSION,
            base_blocks,
        )

        cls._save_intervals_if_changed(
            therapist,
            target_date,
            AvailabilityBlock.BlockType.INCLUSION,
            inclusions,
        )
        cls._save_intervals_if_changed(
            therapist,
            target_date,
            AvailabilityBlock.BlockType.EXCLUSION,
            exclusions,
        )

        if source_block is None:
            return None
        return cls._find_normalized_block(therapist, target_date, source_block)

    @staticmethod
    def _find_normalized_block(therapist, target_date, source_block):
        blocks = list(
            AvailabilityBlock.objects.filter(
                therapist=therapist,
                type=source_block.type,
                specific_date=target_date,
            ).order_by("start_time")
        )
        if not blocks:
            return None

        for block in blocks:
            if (
                block.start_time <= source_block.start_time
                and block.end_time >= source_block.end_time
            ):
                return block
        return blocks[0]

    @staticmethod
    def validate_exclusion(therapist, target_date, start, end):
        if not any(
            overlaps(start, end, block.start_time, block.end_time)
            for block in ScheduleEngine._weekly_base_blocks_queryset(
                therapist, target_date
            )
        ):
            raise ValidationError(
                _("Wykluczenie musi usuwać fragment bazowego grafiku")
            )

    @staticmethod
    def validate_inclusion(therapist, target_date, start, end):
        if any(
            overlaps(start, end, block.start_time, block.end_time)
            for block in ScheduleEngine._weekly_base_blocks_queryset(
                therapist, target_date
            )
        ):
            raise ValidationError(
                _("Dodatkowe godziny nie mogą pokrywać się z bazowym grafikiem")
            )

    @classmethod
    def validate_override(cls, block: AvailabilityBlock):
        if block.type == AvailabilityBlock.BlockType.EXCLUSION:
            cls.validate_exclusion(
                block.therapist,
                block.specific_date,
                block.start_time,
                block.end_time,
            )
        elif block.type == AvailabilityBlock.BlockType.INCLUSION:
            cls.validate_inclusion(
                block.therapist,
                block.specific_date,
                block.start_time,
                block.end_time,
            )
