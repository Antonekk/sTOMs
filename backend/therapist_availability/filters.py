from .models import AvailabilityBlock


def get_weekly_availability_blocks(therapist, day_of_week):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        day_of_week=day_of_week,
        type=AvailabilityBlock.BlockType.BASE,
    ).order_by("start_time")


def filter_weekly_availability_blocks(therapist, day_of_week, start_time, end_time):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        day_of_week=day_of_week,
        start_time__lt=end_time,
        end_time__gt=start_time,
        type=AvailabilityBlock.BlockType.BASE,
    )


def get_override_availability_blocks(therapist, specific_date):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        specific_date=specific_date,
        type__in=[
            AvailabilityBlock.BlockType.INCLUSION,
            AvailabilityBlock.BlockType.EXCLUSION,
        ],
    ).order_by("start_time")
