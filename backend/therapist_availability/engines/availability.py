from datetime import date

from therapist_availability.models import AvailabilityBlock
from therapist_availability.utils import exclude_intervals


class AvailabilityEngine:
    """
    Engine for computing therapist availability blocks
    """

    @staticmethod
    def get_slots(therapist, target_date: date) -> list[dict]:
        """Return raw availability intervals after BASE, EXCLUSION and INCLUSION."""
        day_of_week = target_date.weekday()

        base_blocks = [
            {"start_time": block.start_time, "end_time": block.end_time}
            for block in AvailabilityBlock.objects.filter(
                therapist=therapist,
                type=AvailabilityBlock.BlockType.BASE,
                day_of_week=day_of_week,
            ).order_by("start_time")
        ]

        overrides = AvailabilityBlock.objects.filter(
            therapist=therapist,
            specific_date=target_date,
            type__in=[
                AvailabilityBlock.BlockType.INCLUSION,
                AvailabilityBlock.BlockType.EXCLUSION,
            ],
        ).order_by("start_time")

        inclusion_blocks = [
            {"start_time": block.start_time, "end_time": block.end_time}
            for block in overrides
            if block.type == AvailabilityBlock.BlockType.INCLUSION
        ]
        exclusion_blocks = [
            {"start_time": block.start_time, "end_time": block.end_time}
            for block in overrides
            if block.type == AvailabilityBlock.BlockType.EXCLUSION
        ]

        availability_blocks = sorted(
            base_blocks + inclusion_blocks, key=lambda x: x["start_time"]
        )
        return exclude_intervals(availability_blocks, exclusion_blocks)
