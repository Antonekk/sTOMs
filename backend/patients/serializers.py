from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    birthday = serializers.DateField(source="date_of_birth")

    class Meta:
        model = Patient
        fields = (
            "id",
            "first_name",
            "last_name",
            "birthday",
            "is_primary",
            "is_active",
        )
        read_only_fields = fields


class PatientWriteSerializer(serializers.ModelSerializer):
    birthday = serializers.DateField(source="date_of_birth")
    is_primary = serializers.BooleanField(read_only=True)

    class Meta:
        model = Patient
        fields = (
            "first_name",
            "last_name",
            "birthday",
            "is_primary",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["is_primary"] = False
        return super().create(validated_data)
