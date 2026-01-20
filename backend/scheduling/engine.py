from datetime import datetime

from .filters import get_override_availability_blocks, get_weekly_availability_blocks
from .models import AvailabilityBlock


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
