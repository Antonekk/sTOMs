from rest_framework.permissions import BasePermission


class IsTherapist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "THERAPIST"


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CLIENT"
