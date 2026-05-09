from rest_framework.permissions import BasePermission

from .models import AppUser

# Permissions classes for different roles


class IsTherapist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == AppUser.Role.THERAPIST
        )


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == AppUser.Role.CLIENT


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff and request.user.role == AppUser.Role.ADMIN
