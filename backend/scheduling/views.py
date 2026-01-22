from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from users.permissions import IsTherapist

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

    def create(self, request):
        serializer = WeeklyScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        therapist = request.user.therapist

        with transaction.atomic():
            AvailabilityBlock.objects.filter(
                therapist=therapist, type=AvailabilityBlock.BlockType.WEEKLY
            ).delete()

            for day_of_week, blocks in serializer.validated_data[
                "weekly_schedule"
            ].items():
                for block in blocks:
                    AvailabilityBlock.objects.create(
                        therapist=therapist,
                        type=AvailabilityBlock.BlockType.WEEKLY,
                        day_of_week=day_of_week,
                        start_time=block["start_time"],
                        end_time=block["end_time"],
                    )
        return Response(status=status.HTTP_201_CREATED)


class TherapistScheduleOverride(GenericViewSet):
    permission_classes = [IsTherapist]
    serializer_class = AvailabilityBlockSerializer

    def create(self, request):
        serializer = AvailabilityBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(therapist=request.user.therapist)

        return Response(status=status.HTTP_201_CREATED)
