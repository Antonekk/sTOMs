from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from therapist_availability.models import AvailabilityBlock
from therapist_availability.utils import merge_adjacent_blocks, merge_adjacent_date_blocks, overlaps


class ScheduleEngine:
    @staticmethod
    def validate_base_blocks_overlap(blocks):
        by_day: dict[int, list] = {}
        for block in blocks:
            by_day.setdefault(block["day_of_week"], []).append(block)

        for day_blocks in by_day.values():
            sorted_blocks = sorted(day_blocks, key=lambda x: x["start_time"])
            for index in range(len(sorted_blocks) - 1):
                current = sorted_blocks[index]
                next_block = sorted_blocks[index + 1]
                if current["end_time"] > next_block["start_time"]:
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

    @staticmethod
    def validate_exclusion(therapist, target_date, start, end):
        weekly_blocks = AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=target_date.weekday(),
        )

        if not any(
            overlaps(start, end, block.start_time, block.end_time)
            for block in weekly_blocks
        ):
            raise ValidationError(
                _("Wykluczenie musi usuwać fragment bazowego grafiku")
            )

        exclusion_blocks = AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.EXCLUSION,
            specific_date=target_date,
        )

        if any(
            overlaps(start, end, block.start_time, block.end_time)
            for block in exclusion_blocks
        ):
            raise ValidationError(_("Wykluczenie nie może nakładać się z innym"))

    @staticmethod
    def validate_inclusion(therapist, target_date, start, end):
        weekly_blocks = AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.BASE,
            day_of_week=target_date.weekday(),
        )

        if any(
            overlaps(start, end, block.start_time, block.end_time)
            for block in weekly_blocks
        ):
            raise ValidationError(
                _("Dodatkowe godziny nie mogą pokrywać się z bazowym grafikiem")
            )

        inclusion_blocks = AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.INCLUSION,
            specific_date=target_date,
        )

        if any(
            overlaps(start, end, block.start_time, block.end_time)
            for block in inclusion_blocks
        ):
            raise ValidationError(_("Rozszerzenie nie może nakładać się z innym"))

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

    @classmethod
    @transaction.atomic
    def merge_adjacent_overrides(
        cls,
        therapist,
        target_date,
        block_type,
        source_block=None,
    ):
        blocks = list(
            AvailabilityBlock.objects.filter(
                therapist=therapist,
                type=block_type,
                specific_date=target_date,
            ).order_by("start_time")
        )

        if len(blocks) <= 1:
            return blocks[0] if blocks else None

        merged_ranges = merge_adjacent_date_blocks(
            [
                {
                    "specific_date": block.specific_date,
                    "start_time": block.start_time,
                    "end_time": block.end_time,
                }
                for block in blocks
            ]
        )

        if len(merged_ranges) == len(blocks):
            return source_block or blocks[0]

        AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=block_type,
            specific_date=target_date,
        ).delete()

        new_blocks = AvailabilityBlock.objects.bulk_create(
            [
                AvailabilityBlock(
                    therapist=therapist,
                    type=block_type,
                    specific_date=target_date,
                    start_time=merged_range["start_time"],
                    end_time=merged_range["end_time"],
                )
                for merged_range in merged_ranges
            ]
        )

        if source_block is not None:
            for new_block in new_blocks:
                if (
                    new_block.start_time <= source_block.start_time
                    and new_block.end_time >= source_block.end_time
                ):
                    return new_block

        return new_blocks[0] if new_blocks else None

    @staticmethod
    def validate_override_date(specific_date: date):
        if specific_date < timezone.localdate():
            raise ValidationError(_("Data wyjątku musi być w przyszłości"))
