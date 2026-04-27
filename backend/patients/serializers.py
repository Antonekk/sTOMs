from constance import config
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
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

    def validate(self, attrs):
        request = self.context.get("request")
        if request and self.instance is None:
            active_count = Patient.objects.filter(
                user=request.user, is_active=True
            ).count()
            if active_count >= config.MAX_PATIENTS_PER_CLIENT:
                raise serializers.ValidationError(
                    _(
                        "Można mieć maksymalnie %(max)s aktywnych pacjentów."
                    )
                    % {"max": config.MAX_PATIENTS_PER_CLIENT}
                )
        return attrs

    def _raise_duplicate_patient_error(self, exc, user, validated_data):
        instance = self.instance
        first_name = validated_data.get(
            "first_name", instance.first_name if instance else ""
        ).capitalize()
        last_name = validated_data.get(
            "last_name", instance.last_name if instance else ""
        ).capitalize()
        date_of_birth = validated_data.get(
            "date_of_birth", instance.date_of_birth if instance else None
        )
        queryset = Patient.objects.filter(
            user=user,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
        )
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        existing = queryset.first()
        if existing and not existing.is_active:
            raise serializers.ValidationError(
                _("Profil usunięty — przywróć go zamiast dodawać nowy.")
            ) from exc
        raise serializers.ValidationError(_("Taki pacjent już istnieje.")) from exc

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["is_primary"] = False
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            self._raise_duplicate_patient_error(exc, request.user, validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        try:
            return super().update(instance, validated_data)
        except IntegrityError as exc:
            self._raise_duplicate_patient_error(exc, request.user, validated_data)
