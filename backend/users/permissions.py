from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import AppUser


# Defines permissions for Patients endpoints
class PatientPermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        # Restrict access for therapist to safe methods
        if user.role == AppUser.Role.THERAPIST:
            return request.method in SAFE_METHODS

        # Allow full control for users
        if user.role == AppUser.Role.CLIENT:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == AppUser.Role.THERAPIST:
            return request.method in SAFE_METHODS

        # Allow users full controll for their own objects
        return obj.user == user


# Defines permissions for Therapists endpoints
class TherapistPermissions(BasePermission):
    # Only allow for safe methods
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and request.method in SAFE_METHODS


class IsTherapist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "THERAPIST"


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CLIENT"
