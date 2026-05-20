from rest_framework import serializers


class ConfigSerializer(serializers.Serializer):
    appointment_generation_days = serializers.IntegerField()
    appointment_booking_days = serializers.IntegerField()
    cancellation_window_hours = serializers.IntegerField()
