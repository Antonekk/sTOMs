from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "user",
        "date_of_birth",
    )

    list_filter = ("date_of_birth",)

    search_fields = (
        "first_name",
        "last_name",
        "user__email",
        "user__phone_number",
    )

    ordering = ("last_name", "first_name")
