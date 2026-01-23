from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreatePasswordRetypeSerializer, UserSerializer
from rest_framework import serializers

from .models import Patient, Therapist
from .validators import validate_patient_age_primary

User = get_user_model()


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


class TherapistSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Therapist
        fields = ("id", "full_name", "office")
        read_only_fields = ("id", "full_name", "office")


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
