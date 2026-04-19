from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import AppUser
from users.permissions import IsClient, IsTherapist

from therapist_availability.views import get_therapist_for_user

from .models import Appointment, AppointmentSeries, AppointmentType
from .serializers import (
    AppointmentClientSerializer,
    AppointmentDetailSerializer,
    AppointmentNoteSerializer,
    AppointmentSeriesCreateSerializer,
    AppointmentSeriesDetailSerializer,
    AppointmentSeriesListSerializer,
    AppointmentStatusUpdateSerializer,
    AppointmentTherapistSerializer,
    AppointmentTypeSerializer,
)
from .services.cancellation import CancellationService, CancellationWindowError
from .services.horizon import ensure_horizon, ensure_horizon_for_queryset


class AppointmentTypeListView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        types = AppointmentType.objects.all().order_by("name")
        serializer = AppointmentTypeSerializer(types, many=True)
        return Response(serializer.data)


class ReservationListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        queryset = AppointmentSeries.objects.filter(
            patient__user=self.request.user
        ).select_related(
            "therapist__user",
            "patient",
            "appointment_type",
        )
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by("-start_date")

    def get(self, request):
        queryset = self.get_queryset()
        ensure_horizon_for_queryset(queryset)
        serializer = AppointmentSeriesListSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AppointmentSeriesCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        series = serializer.save()
        ensure_horizon(series)
        response_serializer = AppointmentSeriesDetailSerializer(series)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReservationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get_object(self, request, series_id):
        series = get_object_or_404(
            AppointmentSeries.objects.select_related(
                "therapist__user", "patient", "appointment_type"
            ).prefetch_related("appointments"),
            id=series_id,
            patient__user=request.user,
        )
        ensure_horizon(series)
        return series

    def get(self, request, series_id):
        series = self.get_object(request, series_id)
        serializer = AppointmentSeriesDetailSerializer(series)
        return Response(serializer.data)

    def patch(self, request, series_id):
        series = self.get_object(request, series_id)
        if request.data.get("status") != AppointmentSeries.Status.CANCELED:
            return Response(
                {"detail": "Obsługiwane jest wyłącznie anulowanie rezerwacji."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        CancellationService.cancel_series(series)
        series.refresh_from_db()
        serializer = AppointmentSeriesDetailSerializer(series)
        return Response(serializer.data)


class VisitListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = request.user
        queryset = Appointment.objects.select_related(
            "therapist__user",
            "patient",
            "appointment_series__appointment_type",
        )

        if user.role == AppUser.Role.CLIENT:
            queryset = queryset.filter(patient__user=user)
        elif user.role == AppUser.Role.THERAPIST:
            therapist = get_therapist_for_user(user)
            queryset = queryset.filter(therapist=therapist)
        else:
            queryset = queryset.none()

        include_canceled = request.query_params.get("include_canceled", "").lower() == "true"
        if not include_canceled:
            queryset = queryset.exclude(status=Appointment.Status.CANCELED)

        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        therapist_id = request.query_params.get("therapist_id")
        if therapist_id:
            queryset = queryset.filter(therapist_id=therapist_id)

        return queryset.order_by("appointment_date", "appointment_series__start_time")

    def get_serializer_class(self, request):
        if request.user.role == AppUser.Role.THERAPIST:
            return AppointmentTherapistSerializer
        return AppointmentClientSerializer

    def get(self, request):
        if request.user.role not in (AppUser.Role.CLIENT, AppUser.Role.THERAPIST):
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset(request)
        series_ids = queryset.values_list("appointment_series_id", flat=True).distinct()
        ensure_horizon_for_queryset(
            AppointmentSeries.objects.filter(id__in=series_ids)
        )
        serializer_class = self.get_serializer_class(request)
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)


class VisitDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, appointment_id):
        queryset = Appointment.objects.select_related(
            "therapist__user",
            "patient",
            "appointment_series__appointment_type",
        )
        if request.user.role == AppUser.Role.CLIENT:
            queryset = queryset.filter(patient__user=request.user)
        elif request.user.role == AppUser.Role.THERAPIST:
            therapist = get_therapist_for_user(request.user)
            queryset = queryset.filter(therapist=therapist)
        else:
            queryset = queryset.none()

        return get_object_or_404(queryset, id=appointment_id)

    def get(self, request, appointment_id):
        if request.user.role not in (AppUser.Role.CLIENT, AppUser.Role.THERAPIST):
            return Response(status=status.HTTP_403_FORBIDDEN)

        appointment = self.get_object(request, appointment_id)
        if request.user.role == AppUser.Role.THERAPIST:
            serializer = AppointmentDetailSerializer(appointment)
        else:
            serializer = AppointmentClientSerializer(appointment)
        return Response(serializer.data)


class VisitStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def patch(self, request, appointment_id):
        therapist = get_therapist_for_user(request.user)
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            therapist=therapist,
        )

        serializer = AppointmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]

        if appointment.status != Appointment.Status.SCHEDULED:
            return Response(
                {"detail": "Można zmienić status tylko zaplanowanej wizyty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if new_status == Appointment.Status.COMPLETED:
                CancellationService.mark_completed(appointment)
            elif new_status == Appointment.Status.CANCELED:
                CancellationService.cancel_appointment(appointment, enforce_window=True)
        except CancellationWindowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)

        appointment.refresh_from_db()
        return Response(AppointmentTherapistSerializer(appointment).data)


class VisitCancelView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def patch(self, request, appointment_id):
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient__user=request.user,
            status=Appointment.Status.SCHEDULED,
        )
        try:
            CancellationService.cancel_appointment(appointment, enforce_window=True)
        except CancellationWindowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)

        appointment.refresh_from_db()
        return Response(AppointmentClientSerializer(appointment).data)


class VisitNoteUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def patch(self, request, appointment_id):
        therapist = get_therapist_for_user(request.user)
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            therapist=therapist,
        )

        serializer = AppointmentNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment.notes = serializer.validated_data["notes"]
        appointment.save(update_fields=["notes"])
        return Response(AppointmentTherapistSerializer(appointment).data)
