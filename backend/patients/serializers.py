from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id",
            "user",
            "first_name",
            "last_name",
            "date_of_birth",
            "is_primary",
        )
        read_only_fields = (
            "id",
            "user",
            "is_primary",
        )


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id",
            "first_name",
            "last_name",
            "date_of_birth",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["is_primary"] = False
        return super().create(validated_data)
