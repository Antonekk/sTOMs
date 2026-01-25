from rest_framework import serializers

from .models import AvailabilityBlock


class TimeRangeBlockSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, attrs):
        super().validate(attrs)

        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError("Invalid time range")

        return attrs


class WeeklyScheduleSerializer(serializers.Serializer):
    """
    weekly_schedule expected format:
    - key = day of the week (0-6)
    - value = list[TimeRangeBlock]
    """

    weekly_schedule = serializers.DictField(
        child=TimeRangeBlockSerializer(many=True), allow_empty=True
    )

    def validate_weekly_schedule(self, attrs):
        """
        Override to:
        - validate schema
        - ensure no overlaping blocks
        """

        validated_attrs = {}

        for day_of_week, blocks in attrs.items():
            # Validate key
            try:
                day_of_week = int(day_of_week)
            except ValueError:
                raise serializers.ValidationError("Invalid day of the week format")

            if day_of_week < 0 or day_of_week > 6:
                raise serializers.ValidationError("Invalid day of the week")

            # Ensure no overlaping blocks
            sorted_blocks = sorted(blocks, key=lambda x: x["start_time"])

            for i in range(len(sorted_blocks) - 1):
                current_block = sorted_blocks[i]
                next_block = sorted_blocks[i + 1]

                if current_block["end_time"] >= next_block["start_time"]:
                    raise serializers.ValidationError("Overlaping blocks")

            validated_attrs[day_of_week] = sorted_blocks

        return validated_attrs


class AvailabilityBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityBlock
        fields = (
            "id",
            "therapist",
            "specific_date",
            "start_time",
            "end_time",
            "availability_type",
        )
        read_only_fields = ["id", "therapist"]
