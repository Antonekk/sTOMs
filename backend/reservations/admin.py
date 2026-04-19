from django.contrib import admin

from .models import Appointment, AppointmentSeries, AppointmentType


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "duration_time_minutes",
        "price",
        "is_periodic",
    )
    search_fields = ("name",)


class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    readonly_fields = ("appointment_date", "status", "final_price")


@admin.register(AppointmentSeries)
class AppointmentSeriesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "therapist",
        "patient",
        "appointment_type",
        "start_date",
        "start_time",
        "status",
    )
    list_filter = ("status", "appointment_type")
    inlines = [AppointmentInline]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "appointment_date",
        "therapist",
        "patient",
        "status",
        "final_price",
    )
    list_filter = ("status", "appointment_date")
