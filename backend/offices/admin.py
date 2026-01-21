from django.contrib import admin

from .models import Localization, Office


@admin.register(Localization)
class LocalizationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "postal_code", "address")
    list_filter = ("city",)
    search_fields = ("name", "city", "postal_code", "address")
    ordering = ("city", "name")


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("localization", "room_number")
    list_filter = ("localization",)
    search_fields = ("localization__name", "room_number")
    ordering = ("localization", "room_number")
