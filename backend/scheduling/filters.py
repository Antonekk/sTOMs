from .models import AvailabilityBlock


# Get all availability blocks for specified day ou the week
def get_weekly_availability_blocks(therapist, day_of_week):
    return AvailabilityBlock.objects.filter(
        therapist=therapist,
        day_of_week=day_of_week,
        availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY,
    ).order_by("start_time")


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
