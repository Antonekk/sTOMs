from django.contrib import admin

from .models import AvailabilityBlock, Therapist


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ("user", "office")
    list_filter = ("office",)
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )


@admin.register(AvailabilityBlock)
class AvailabilityBlockAdmin(admin.ModelAdmin):
    list_display = (
        "therapist",
        "type",
        "day_of_week",
        "specific_date",
        "start_time",
        "end_time",
    )
    list_filter = ("type", "day_of_week", "specific_date")
