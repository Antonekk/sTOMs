from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .filters import get_override_availability_blocks, get_weekly_availability_blocks
from .models import AvailabilityBlock
from .utils import overlaps


# Merges date and time into datetime object
def merge_to_datetime(date, time):
    return datetime.combine(date, time)


# Performs exclusion on availability_blocks
# This utility assumes that both blocks sets are ordered by start_time
def exclude_from_availability_blocks(availability_blocks, exclusion_blocks):
    result = []
    ptr = 0

    for block in availability_blocks:
        start_time, end_time = block["start_time"], block["end_time"]

        while (
            ptr < len(exclusion_blocks)
            and exclusion_blocks[ptr]["start_time"] <= start_time
        ):
            ptr += 1

        current_start_time = start_time

        while (
            ptr < len(exclusion_blocks)
            and exclusion_blocks[ptr]["start_time"] < end_time
        ):
            exclusion_block = exclusion_blocks[ptr]

            if exclusion_block["start_time"] > current_start_time:
                result.append(
                    {
                        "start_time": current_start_time,
                        "end_time": exclusion_block["start_time"],
                    }
                )
            current_start_time = max(start_time, exclusion_block["end_time"])
            if current_start_time >= end_time:
                break
            ptr += 1

        if current_start_time < end_time:
            result.append(
                {
                    "start_time": current_start_time,
                    "end_time": end_time,
                }
            )
    return result


@transaction.atomic
def replace_weekly_schedule(therapist, weekly_schedule):
    AvailabilityBlock.objects.filter(
        therapist=therapist, type=AvailabilityBlock.BlockType.WEEKLY
    ).delete()

    blocks = []
    for block in weekly_schedule:
        blocks.append(
            AvailabilityBlock(
                therapist=therapist,
                availability_type=AvailabilityBlock.BlockType.WEEKLY,
                day_of_week=block["day_of_week"],
                start_time=block["start_time"],
                end_time=block["end_time"],
            )
        )
    AvailabilityBlock.objects.bulk_create(blocks)
    return blocks


def create_override_availability_block(therapist, override_block):
    block = AvailabilityBlock(
        therapist=therapist,
        availability_type=override_block["availability_type"],
        specific_date=override_block["specific_date"],
        start_time=override_block["start_time"],
        end_time=override_block["end_time"],
    )
    block.save()
    return block


# Validates exclusion rules
def validate_exclusion(therapist, date, start, end):
    weekly_blocks = AvailabilityBlock.objects.filter(
        therapist=therapist,
        availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
        day_of_week=date.weekday(),
    )

    if not any(overlaps(start, end, w.start_time, w.end_time) for w in weekly_blocks):
        raise ValidationError(_("Wykluczenie musi usuwać fragment bazowego grafiku"))

    exclusion_blocks = AvailabilityBlock.objects.filter(
        therapist=therapist,
        availability_type=AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
        specific_date=date,
    )

    if any(overlaps(start, end, e.start_time, e.end_time) for e in exclusion_blocks):
        raise ValidationError(_("Wykluczenie nie może przecinać się z innym exclusion"))


# validates inclusion rules
def validate_inclusion(therapist, date, start, end):
    weekly_blocks = AvailabilityBlock.objects.filter(
        therapist=therapist,
        availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
        day_of_week=date.weekday(),
    )

    if not weekly_blocks.exists():
        raise ValidationError(_("Nie można dodać rozszerzenia bez bazowego grafiku"))

    if not any(start < w.start_time or end > w.end_time for w in weekly_blocks):
        raise ValidationError(_("Rozszerzenie musi rozszerzać bazowy grafik"))

    inclusion_blocks = AvailabilityBlock.objects.filter(
        therapist=therapist,
        availability_type=AvailabilityBlock.AvailabilityBlockType.INCLUSION,
        specific_date=date,
    )

    if any(overlaps(start, end, i.start_time, i.end_time) for i in inclusion_blocks):
        raise ValidationError(
            _("Rozszerzenie nie może przecinać się z innym rozszerzeniami")
        )


def validate_override(block: AvailabilityBlock):
    if block.availability_type == AvailabilityBlock.AvailabilityBlockType.EXCLUSION:
        validate_exclusion(
            therapist=block.therapist,
            date=block.specific_date,
            start=block.start_time,
            end=block.end_time,
        )

    if block.availability_type == AvailabilityBlock.AvailabilityBlockType.INCLUSION:
        validate_inclusion(
            therapist=block.therapist,
            date=block.specific_date,
            start=block.start_time,
            end=block.end_time,
        )


# Generate availability blocks for a specific date
def generate_daily_availability_blocks(therapist, date):
    day_of_week = date.weekday()

    weekly_blocks = [
        {
            "start_time": block.start_time,
            "end_time": block.end_time,
        }
        for block in get_weekly_availability_blocks(therapist, day_of_week)
    ]

    override_blocks = get_override_availability_blocks(therapist, date)

    inclusion_blocks = [
        {
            "start_time": block.start_time,
            "end_time": block.end_time,
        }
        for block in override_blocks
        if block.availability_type == AvailabilityBlock.AvailabilityBlockType.INCLUSION
    ]

    exclusion_blocks = [
        {
            "start_time": block.start_time,
            "end_time": block.end,
        }
        for block in override_blocks
        if block.availability_type == AvailabilityBlock.AvailabilityBlockType.EXCLUSION
    ]

    # This is actually faster than merge with assumption that lists contain < around 10000 elements which in this case will be sufficient
    availability_blocks = sorted(
        weekly_blocks + inclusion_blocks, key=lambda x: x["start_time"]
    )
    availability_blocks = exclude_from_availability_blocks(
        availability_blocks, exclusion_blocks
    )

    # TODO: Add appointment exclusion

    return availability_blocks
