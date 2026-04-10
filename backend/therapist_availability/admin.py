from django.contrib import admin

from .models import Therapist


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = (
        "therapist",
        "office",
    )
    list_filter = ("office",)
    search_fields = (
        "therapist__email",
        "therapist__first_name",
        "therapist__last_name",
    )
