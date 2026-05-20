from constance import config
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.permissions import IsClient

from .models import Patient
from .serializers import PatientSerializer, PatientWriteSerializer


class PatientViewSet(ModelViewSet):
    permission_classes = [IsClient]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return PatientWriteSerializer
        return PatientSerializer

    def get_queryset(self):
        queryset = Patient.objects.filter(user=self.request.user)
        if self.action == "restore":
            return queryset.filter(is_active=False)
        if self.action == "list":
            is_active = self.request.query_params.get("is_active")
            if is_active is not None:
                queryset = queryset.filter(
                    is_active=is_active.lower() in ("true", "1")
                )
            else:
                queryset = queryset.filter(is_active=True)
            return queryset
        return queryset.filter(is_active=True)

    def _active_patient_count(self):
        return Patient.objects.filter(
            user=self.request.user, is_active=True
        ).count()

    def _patient_limit_reached_response(self):
        return Response(
            {
                "detail": _(
                    "Można mieć maksymalnie %(max)s aktywnych pacjentów."
                )
                % {"max": config.MAX_PATIENTS_PER_CLIENT}
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_primary=False)

    def create(self, request, *args, **kwargs):
        if self._active_patient_count() >= config.MAX_PATIENTS_PER_CLIENT:
            return self._patient_limit_reached_response()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        patient = serializer.instance
        return Response(
            PatientSerializer(patient).data,
            status=status.HTTP_201_CREATED,
        )

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

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        patient = self.get_object()
        if self._active_patient_count() >= config.MAX_PATIENTS_PER_CLIENT:
            return self._patient_limit_reached_response()
        patient.is_active = True
        patient.save(update_fields=["is_active"])
        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)
