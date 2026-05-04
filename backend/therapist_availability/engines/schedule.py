from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from therapist_availability.models import AvailabilityBlock
from therapist_availability.utils import merge_adjacent_blocks, overlaps


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

    @staticmethod
    def validate_override_date(specific_date: date):
        if specific_date < timezone.localdate():
            raise ValidationError(_("Data wyjątku musi być w przyszłości"))
