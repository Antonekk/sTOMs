from constance import config
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.viewsets import ModelViewSet
from users.permissions import IsClient

from .cache_utils import (
    get_cached_patient_detail,
    get_cached_patient_list,
    invalidate_patient_cache,
    set_cached_patient_detail,
    set_cached_patient_list,
)
from .models import Patient
from .serializers import PatientSerializer, PatientWriteSerializer

_PATIENT_ACTIONS = {
    "list",
    "retrieve",
    "create",
    "update",
    "destroy",
    "restore"
}


class PatientViewSet(ModelViewSet):
    permission_classes = [IsClient]
    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def get_throttles(self):
        if self.action in _PATIENT_ACTIONS:
            self.throttle_scope = "patients"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return PatientWriteSerializer
        return PatientSerializer

    def get_queryset(self):
        queryset = Patient.objects.filter(user=self.request.user)
        if self.action == "restore":
            return queryset.filter(is_active=False)
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

    def list(self, request, *args, **kwargs):
        cached = get_cached_patient_list(request.user.id)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        set_cached_patient_list(request.user.id, response.data)
        return response

    def retrieve(self, request, *args, **kwargs):
        patient = self.get_object()
        cached = get_cached_patient_detail(request.user.id, patient.id)
        if cached is not None:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        set_cached_patient_detail(request.user.id, patient.id, response.data)
        return response

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_primary=False)

    def create(self, request, *args, **kwargs):
        if self._active_patient_count() >= config.MAX_PATIENTS_PER_CLIENT:
            return self._patient_limit_reached_response()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        patient = serializer.instance
        invalidate_patient_cache(request.user.id, patient.id)
        return Response(
            PatientSerializer(patient).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        invalidate_patient_cache(request.user.id, kwargs["pk"])
        return response

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        if patient.is_primary:
            return Response(
                {"detail": "Nie można usunąć głównego profilu pacjenta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        patient.is_active = False
        patient.save(update_fields=["is_active"])
        invalidate_patient_cache(request.user.id, patient.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        patient = self.get_object()
        if self._active_patient_count() >= config.MAX_PATIENTS_PER_CLIENT:
            return self._patient_limit_reached_response()
        patient.is_active = True
        patient.save(update_fields=["is_active"])
        invalidate_patient_cache(request.user.id, patient.id)
        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)
