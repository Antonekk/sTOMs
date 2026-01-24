from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from users.permissions import IsTherapist

from .engine import replace_weekly_schedule, validate_override
from .models import AvailabilityBlock
from .serializers import AvailabilityBlockSerializer, WeeklyScheduleSerializer


class TherapistScheduleView(GenericViewSet):
    permission_classes = [IsTherapist]
    serializer_class = WeeklyScheduleSerializer

    def list(self, request):
        therapist = request.user.therapist
        blocks = AvailabilityBlock.objects.filter(
            therapist=therapist, type=AvailabilityBlock.BlockType.WEEKLY
        )

        response_data = {}
        for block in blocks:
            response_data.setdefault(block.day_of_week, []).append(
                {
                    "start_time": block.start_time,
                    "end_time": block.end_time,
                }
            )

        return Response(response_data)

    @action(detail=False, methods=["post, put"])
    def replace_weekly_schedule(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        therapist = request.user.therapist

        replace_weekly_schedule(therapist, serializer.validated_data["weekly_schedule"])

        with transaction.atomic():
            AvailabilityBlock.objects.filter(
                therapist=therapist, type=AvailabilityBlock.BlockType.WEEKLY
            ).delete()

            blocks_to_create = [
                AvailabilityBlock(
                    therapist=therapist,
                    type=AvailabilityBlock.BlockType.WEEKLY,
                    day_of_week=day_of_week,
                    start_time=block["start_time"],
                    end_time=block["end_time"],
                )
                for day_of_week, blocks in serializer.validated_data[
                    "weekly_schedule"
                ].items()
                for block in blocks
            ]
            AvailabilityBlock.objects.bulk_create(blocks_to_create)
        return Response(status=status.HTTP_201_CREATED)


class TherapistScheduleOverride(ModelViewSet):
    permission_classes = [IsTherapist]
    serializer_class = AvailabilityBlockSerializer
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return AvailabilityBlock.objects.filter(
            therapist=self.request.user,
        ).exclude(availability_type=AvailabilityBlock.AvailabilityBlockType.WEEKLY)

    def perform_create(self, serializer):
        block = AvailabilityBlock(
            therapist=self.request.user,
            **serializer.validated_data,
        )
        validate_override(block)
        block.full_clean()
        block.save()
