from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AppUser, Patient


class PatientInline(admin.TabularInline):
    model = Patient
    extra = 0
    min_num = 0
    show_change_link = True


@admin.register(AppUser)
class AppUserAdmin(BaseUserAdmin):
    model = AppUser

    inlines = (PatientInline,)

    list_display = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_verified",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_verified",
    )

    search_fields = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
    )

    ordering = ("email",)

    readonly_fields = ("id", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                )
            },
        ),
        (
            _("Role & Status"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_verified",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("date_joined",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


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
