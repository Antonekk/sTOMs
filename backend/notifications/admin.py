from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "creation_timestamp", "is_read")
    list_filter = ("is_read",)
    search_fields = ("title", "description", "user__email")
    readonly_fields = ("id", "creation_timestamp")
