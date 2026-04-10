from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import AppUser
from users.permissions import PatientPermissions

from .models import Patient
from .serializers import PatientCreateSerializer, PatientSerializer


class PatientViewSet(ModelViewSet):
    permission_classes = [PatientPermissions]

    def get_serializer_class(self):
        if self.action == "create":
            return PatientCreateSerializer
        return PatientSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.role == AppUser.Role.THERAPIST:
            return Patient.objects.all()

        return Patient.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_primary=False)

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        if patient.is_primary:
            return Response(
                {"detail": "Nie można usunąć głównego profilu pacjenta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
