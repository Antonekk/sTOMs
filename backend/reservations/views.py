from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import AppUser
from users.permissions import IsClient, IsTherapist

from therapist_availability.models import Therapist
from therapist_availability.views import get_therapist_for_user

from .models import Appointment, AppointmentSeries, AppointmentType
from .serializers import (
    AppointmentClientSerializer,
    AppointmentNoteSerializer,
    AppointmentSeriesCreateSerializer,
    AppointmentSeriesDetailSerializer,
    AppointmentSeriesListSerializer,
    AppointmentStatusUpdateSerializer,
    AppointmentTherapistSerializer,
    AppointmentTypeSerializer,
    BookableSlotSerializer,
    BookableTimeOptionsSerializer,
    BookingTherapistSerializer,
)
from .engines.cancellation import CancellationEngine, CancellationWindowError
from .engines.slots import BookableSlotsEngine
from .slot_search import parse_slot_search_params

APPOINTMENT_SELECT_RELATED = (
    "therapist__user",
    "therapist__office__localization",
    "patient",
    "appointment_series__appointment_type",
)

SERIES_SELECT_RELATED = (
    "therapist__user",
    "therapist__office__localization",
    "patient",
    "appointment_type",
)


class BookableSlotPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


def _appointments_for_user(user):
    queryset = Appointment.objects.select_related(*APPOINTMENT_SELECT_RELATED)
    if user.role == AppUser.Role.CLIENT:
        return queryset.filter(patient__user=user)
    if user.role == AppUser.Role.THERAPIST:
        return queryset.filter(therapist=get_therapist_for_user(user))
    return queryset.none()


def _filter_appointments(queryset, request):
    if request.query_params.get("include_canceled", "").lower() != "true":
        queryset = queryset.exclude(status=Appointment.Status.CANCELED)
    status_filter = request.query_params.get("status")
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    therapist_id = request.query_params.get("therapist_id")
    if therapist_id:
        queryset = queryset.filter(therapist_id=therapist_id)
    return queryset.order_by("appointment_date", "appointment_series__start_time")


def _list_bookable_slots(request, *, include_time_filters=True):
    params = parse_slot_search_params(
        request.query_params,
        include_time_filters=include_time_filters,
    )
    return BookableSlotsEngine.list_slots(
        appointment_type=params.appointment_type,
        date_from=params.date_from,
        date_to=params.date_to,
        therapist_id=params.therapist_id,
        office_id=params.office_id,
        day_of_week=params.day_of_week,
        time_from=params.time_from,
        time_to=params.time_to,
    )


class TherapistListView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        therapists = Therapist.objects.select_related(
            "user", "office", "office__localization"
        ).order_by("user__last_name", "user__first_name")
        return Response(BookingTherapistSerializer(therapists, many=True).data)


class BookableSlotListView(APIView):
    permission_classes = [IsAuthenticated, IsClient]
    pagination_class = BookableSlotPagination

    def get(self, request):
        slots = _list_bookable_slots(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(slots, request, view=self)
        return paginator.get_paginated_response(
            BookableSlotSerializer(page, many=True).data
        )


class BookableTimeOptionsView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        slots = _list_bookable_slots(request, include_time_filters=False)
        start_times = sorted({slot["start_time"].strftime("%H:%M") for slot in slots})
        end_times = sorted({slot["end_time"].strftime("%H:%M") for slot in slots})
        return Response(
            BookableTimeOptionsSerializer(
                {"start_times": start_times, "end_times": end_times}
            ).data
        )


class AppointmentTypeListView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        types = AppointmentType.objects.all().order_by("name")
        return Response(AppointmentTypeSerializer(types, many=True).data)


class ReservationListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        queryset = AppointmentSeries.objects.filter(
            patient__user=request.user
        ).select_related(*SERIES_SELECT_RELATED)
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        serializer = AppointmentSeriesListSerializer(
            queryset.order_by("-start_date"), many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = AppointmentSeriesCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        series = serializer.save()
        return Response(
            AppointmentSeriesDetailSerializer(series).data,
            status=status.HTTP_201_CREATED,
        )


class ReservationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def _get_series(self, request, series_id):
        return get_object_or_404(
            AppointmentSeries.objects.select_related(*SERIES_SELECT_RELATED).prefetch_related(
                "appointments"
            ),
            id=series_id,
            patient__user=request.user,
        )

    def get(self, request, series_id):
        return Response(
            AppointmentSeriesDetailSerializer(self._get_series(request, series_id)).data
        )

    def patch(self, request, series_id):
        series = self._get_series(request, series_id)
        if request.data.get("status") != AppointmentSeries.Status.CANCELED:
            return Response(
                {"detail": "Obsługiwane jest wyłącznie anulowanie rezerwacji."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        CancellationEngine.cancel_series(series, canceled_by=AppUser.Role.CLIENT)
        series.refresh_from_db()
        return Response(AppointmentSeriesDetailSerializer(series).data)


class VisitListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in (AppUser.Role.CLIENT, AppUser.Role.THERAPIST):
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = _filter_appointments(_appointments_for_user(request.user), request)
        serializer_class = (
            AppointmentTherapistSerializer
            if request.user.role == AppUser.Role.THERAPIST
            else AppointmentClientSerializer
        )
        return Response(serializer_class(queryset, many=True).data)


class VisitDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        if request.user.role not in (AppUser.Role.CLIENT, AppUser.Role.THERAPIST):
            return Response(status=status.HTTP_403_FORBIDDEN)

        appointment = get_object_or_404(
            _appointments_for_user(request.user), id=appointment_id
        )
        serializer_class = (
            AppointmentTherapistSerializer
            if request.user.role == AppUser.Role.THERAPIST
            else AppointmentClientSerializer
        )
        return Response(serializer_class(appointment).data)


class VisitStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def patch(self, request, appointment_id):
        therapist = get_therapist_for_user(request.user)
        appointment = get_object_or_404(
            Appointment, id=appointment_id, therapist=therapist
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
                CancellationEngine.mark_completed(appointment)
            elif new_status == Appointment.Status.CANCELED:
                CancellationEngine.cancel_appointment(
                    appointment,
                    enforce_window=True,
                    canceled_by=AppUser.Role.THERAPIST,
                )
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
            CancellationEngine.cancel_appointment(
                appointment,
                enforce_window=True,
                canceled_by=AppUser.Role.CLIENT,
            )
        except CancellationWindowError as exc:
            return Response({"detail": str(exc.detail)}, status=exc.status_code)

        appointment.refresh_from_db()
        return Response(AppointmentClientSerializer(appointment).data)


class VisitNoteUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def patch(self, request, appointment_id):
        therapist = get_therapist_for_user(request.user)
        appointment = get_object_or_404(
            Appointment, id=appointment_id, therapist=therapist
        )

        serializer = AppointmentNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment.notes = serializer.validated_data["notes"]
        appointment.save(update_fields=["notes"])
        return Response(AppointmentTherapistSerializer(appointment).data)
