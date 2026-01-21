from rest_framework import serializers

from .models import Localization, Office


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ("id", "room_number")
        read_only_fields = fields


class LocalizationSerializer(serializers.ModelSerializer):
    offices = OfficeSerializer(many=True, read_only=True)

    class Meta:
        model = Localization
        fields = ("id", "name", "city", "postal_code", "address", "offices")
        read_only_fields = fields
