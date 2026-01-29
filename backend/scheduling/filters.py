from .models import AvailabilityBlock


# Get all availability blocks for specified day ou the week
def get_weekly_availability_blocks(therapist, day_of_week):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        day_of_week=day_of_week,
        availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
    ).order_by("start_time")


def filter_weekly_availability_blocks(therapist, day_of_week, start_time, end_time):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        day_of_week=day_of_week,
        start_time__lt=end_time,
        end_time__gt=start_time,
        availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
    )


# Get all availability override blocks for specified date
def get_override_availability_blocks(therapist, specific_date):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        specific_date=specific_date,
        availability_type__in=[
            AvailabilityBlock.AvailabilityBlockType.INCLUSION,
            AvailabilityBlock.AvailabilityBlockType.EXCLUSION,
        ],
    ).order_by("start_time")
