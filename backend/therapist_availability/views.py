from datetime import date, timedelta

from constance import config
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.permissions import IsClient, IsTherapist

from .models import AvailabilityBlock, Therapist
from .serializers import (
    AvailabilityDaySerializer,
    BaseScheduleResponseSerializer,
    BaseScheduleSerializer,
    OverrideBlockSerializer,
    TherapistSerializer,
)
from reservations.services.cancellation import CancellationService

from .engines import AvailabilityEngine, ScheduleEngine
from .utils import merge_adjacent_blocks


def get_therapist_for_user(user) -> Therapist:
    therapist = Therapist.objects.filter(user=user).select_related("office").first()
    if therapist is None:
        raise NotFound("Profil terapeuty nie istnieje.")
    return therapist


class TherapistViewSet(ReadOnlyModelViewSet):
    serializer_class = TherapistSerializer
    queryset = Therapist.objects.select_related("user", "office")
    permission_classes = [IsAuthenticated, IsTherapist]


class SelfScheduleView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def get(self, request):
        therapist = get_therapist_for_user(request.user)
        blocks = AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.BASE,
        ).order_by("day_of_week", "start_time")
        payload = {
            "blocks": merge_adjacent_blocks(
                [
                    {
                        "day_of_week": block.day_of_week,
                        "start_time": block.start_time,
                        "end_time": block.end_time,
                    }
                    for block in blocks
                ]
            )
        }
        serializer = BaseScheduleResponseSerializer(payload)
        return Response(serializer.data)

    def put(self, request):
        serializer = BaseScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        therapist = get_therapist_for_user(request.user)
        ScheduleEngine.replace_base_schedule(
            therapist, serializer.validated_data["blocks"]
        )
        CancellationService.cancel_conflicting_appointments(therapist)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SelfScheduleOverrideView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def get(self, request):
        therapist = get_therapist_for_user(request.user)
        blocks = AvailabilityBlock.objects.filter(
            therapist=therapist,
            type__in=[
                AvailabilityBlock.BlockType.INCLUSION,
                AvailabilityBlock.BlockType.EXCLUSION,
            ],
            specific_date__gte=timezone.localdate(),
        ).order_by("specific_date", "start_time")
        serializer = OverrideBlockSerializer(blocks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OverrideBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        therapist = get_therapist_for_user(request.user)
        block = AvailabilityBlock(therapist=therapist, **serializer.validated_data)
        try:
            ScheduleEngine.validate_override(block)
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise ValidationError(exc.message_dict) from exc
            raise ValidationError({"detail": str(exc.message or exc)}) from exc
        block.save()

        if block.type == AvailabilityBlock.BlockType.EXCLUSION:
            CancellationService.cancel_conflicting_appointments(
                therapist, target_date=block.specific_date
            )

        return Response(
            OverrideBlockSerializer(block).data,
            status=status.HTTP_201_CREATED,
        )


class SelfScheduleOverrideDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTherapist]

    def delete(self, request, block_id):
        therapist = get_therapist_for_user(request.user)
        block = get_object_or_404(
            AvailabilityBlock,
            id=block_id,
            therapist=therapist,
            type__in=[
                AvailabilityBlock.BlockType.INCLUSION,
                AvailabilityBlock.BlockType.EXCLUSION,
            ],
        )
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailabilityListView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        today = timezone.localdate()
        date_from = self._parse_date(request.query_params.get("date_from"), today)
        date_to = self._parse_date(
            request.query_params.get("date_to"),
            today + timedelta(days=7),
        )

        if date_from > date_to:
            raise ValidationError({"date_to": "Data końcowa musi być po dacie początkowej."})

        max_days = getattr(config, "AVAILABILITY_MAX_RANGE_DAYS", 30)
        if (date_to - date_from).days > max_days:
            raise ValidationError(
                {
                    "date_to": (
                        f"Maksymalny zakres zapytań to {max_days} dni."
                    )
                }
            )

        therapists = Therapist.objects.select_related(
            "user", "office", "office__localization"
        )
        therapist_id = request.query_params.get("therapist_id")
        office_id = request.query_params.get("office_id")
        day_of_week = request.query_params.get("day_of_week")

        if therapist_id:
            therapists = therapists.filter(id=therapist_id)
        if office_id:
            therapists = therapists.filter(office_id=office_id)

        results = []
        current = date_from
        while current <= date_to:
            if day_of_week is not None and current.weekday() != int(day_of_week):
                current += timedelta(days=1)
                continue

            for therapist in therapists:
                slots = AvailabilityEngine.get_slots(therapist, current)
                if not slots:
                    continue

                office = therapist.office
                localization = None
                if office is not None:
                    localization = str(office.localization)

                results.append(
                    {
                        "therapist_id": therapist.id,
                        "therapist_name": therapist.user.get_full_name(),
                        "office_id": office.id if office else None,
                        "localization": localization,
                        "date": current,
                        "slots": slots,
                    }
                )
            current += timedelta(days=1)

        serializer = AvailabilityDaySerializer(results, many=True)
        return Response(serializer.data)

    @staticmethod
    def _parse_date(value, default: date) -> date:
        if not value:
            return default
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError({"date": "Nieprawidłowy format daty (YYYY-MM-DD)."}) from exc
