from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreatePasswordRetypeSerializer, UserSerializer
from rest_framework import serializers

from patients.models import Patient
from patients.serializers import PatientSerializer

from .validators import validate_patient_age_primary

User = get_user_model()


class AppUserSerializer(UserSerializer):
    patients = PatientSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("patients", "role")


class AppUserCreatePasswordRetypeSerializer(UserCreatePasswordRetypeSerializer):
    date_of_birth = serializers.DateField(write_only=True)

    class Meta:
        model = User
        fields = UserCreatePasswordRetypeSerializer.Meta.fields + ("date_of_birth",)

    def validate_date_of_birth(self, value):
        return validate_patient_age_primary(value)

    # Override validation to store date_of_birth for creating Patient
    def validate(self, attrs):
        self.context["date_of_birth"] = attrs.pop("date_of_birth")
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")

        user = super().create(validated_data)

        Patient.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=self.context["date_of_birth"],
            is_primary=True,
        )

        return user
