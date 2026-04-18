from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.permissions import IsClient

from .models import Patient
from .serializers import PatientSerializer, PatientWriteSerializer


class PatientViewSet(ModelViewSet):
    permission_classes = [IsClient]
    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return PatientWriteSerializer
        return PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_primary=False)

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        if patient.is_primary:
            return Response(
                {"detail": "Nie można usunąć głównego profilu pacjenta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        patient.is_active = False
        patient.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
