from datetime import date

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import AvailabilityBlock, Therapist


class TherapistSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Therapist
        fields = ("id", "full_name", "office")
        read_only_fields = ("id", "full_name", "office")

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class BaseScheduleBlockSerializer(serializers.Serializer):
    day_of_week = serializers.IntegerField(min_value=0, max_value=6)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError("Nieprawidłowy przedział czasu")
        return attrs


class BaseScheduleSerializer(serializers.Serializer):
    blocks = BaseScheduleBlockSerializer(many=True)

    def validate_blocks(self, blocks):
        by_day: dict[int, list] = {}
        for block in blocks:
            by_day.setdefault(block["day_of_week"], []).append(block)

        for day_blocks in by_day.values():
            sorted_blocks = sorted(day_blocks, key=lambda item: item["start_time"])
            for index in range(len(sorted_blocks) - 1):
                current = sorted_blocks[index]
                next_block = sorted_blocks[index + 1]
                if current["end_time"] > next_block["start_time"]:
                    raise serializers.ValidationError(
                        "Nakładające się bloki w tym samym dniu tygodnia"
                    )
        return blocks


class BaseScheduleResponseSerializer(serializers.Serializer):
    blocks = BaseScheduleBlockSerializer(many=True)


class OverrideBlockSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=[
            AvailabilityBlock.BlockType.INCLUSION,
            AvailabilityBlock.BlockType.EXCLUSION,
        ]
    )

    class Meta:
        model = AvailabilityBlock
        fields = ("id", "type", "specific_date", "start_time", "end_time")
        read_only_fields = ("id",)

    def validate_specific_date(self, value: date):
        if value < timezone.localdate():
            raise serializers.ValidationError("Data wyjątku musi być w przyszłości")
        return value

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError("Nieprawidłowy przedział czasu")
        return attrs


class AvailabilitySlotSerializer(serializers.Serializer):
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")


class AvailabilityDaySerializer(serializers.Serializer):
    therapist_id = serializers.UUIDField()
    therapist_name = serializers.CharField()
    office_id = serializers.UUIDField(allow_null=True)
    localization = serializers.CharField(allow_null=True)
    date = serializers.DateField()
    slots = AvailabilitySlotSerializer(many=True)
