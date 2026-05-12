from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .exceptions import ConflictError

from patients.models import Patient
from therapist_availability.models import Therapist

from .models import Appointment, AppointmentSeries, AppointmentType
from .engines.booking import BookingEngine
from .engines.collision import CollisionDetectionEngine
from .engines.generation import AppointmentGenerationEngine
from .engines.horizon import ensure_horizon

from notifications.engine import NotificationEngine

WEEKDAY_LABELS = [
    "poniedziałek",
    "wtorek",
    "środa",
    "czwartek",
    "piątek",
    "sobota",
    "niedziela",
]


class AppointmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentType
        fields = (
            "id",
            "name",
            "duration_time_minutes",
            "price",
            "is_periodic",
        )


class AppointmentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ("id", "appointment_date", "status", "final_price")


class AppointmentSeriesListSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source="therapist.user.get_full_name", read_only=True)
    patient_name = serializers.SerializerMethodField()
    appointment_type_name = serializers.CharField(source="appointment_type.name", read_only=True)
    recurrence_display = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentSeries
        fields = (
            "id",
            "status",
            "therapist_name",
            "patient_name",
            "appointment_type_name",
            "start_time",
            "end_time",
            "start_date",
            "recurrence_display",
        )

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_recurrence_display(self, obj):
        if not obj.is_weekly:
            return None
        weekday = WEEKDAY_LABELS[obj.start_date.weekday()]
        return f"Co tydzień w {weekday}"


class AppointmentSeriesDetailSerializer(AppointmentSeriesListSerializer):
    appointments = AppointmentSummarySerializer(many=True, read_only=True)

    class Meta(AppointmentSeriesListSerializer.Meta):
        fields = AppointmentSeriesListSerializer.Meta.fields + ("appointments",)


class AppointmentSeriesCreateSerializer(serializers.Serializer):
    therapist_id = serializers.UUIDField()
    patient_id = serializers.UUIDField()
    appointment_type_id = serializers.UUIDField()
    start_time = serializers.TimeField()
    start_date = serializers.DateField()
    is_weekly = serializers.BooleanField(default=False)

    def _validate_occurrence(self, therapist, occurrence_date, start_time, end_time):
        from django.core.exceptions import ValidationError as DjangoValidationError

        try:
            BookingEngine.validate_slot(therapist, occurrence_date, start_time, end_time)
        except DjangoValidationError as exc:
            message = str(exc.message or exc)
            if "zajęty" in message or "koliduje" in message:
                raise ConflictError() from exc
            if hasattr(exc, "message_dict"):
                raise ValidationError(exc.message_dict) from exc
            raise ValidationError({"detail": message}) from exc

    def validate(self, attrs):
        therapist = Therapist.objects.filter(id=attrs["therapist_id"]).first()
        if therapist is None:
            raise ValidationError({"therapist_id": "Terapeuta nie istnieje."})

        patient = Patient.objects.filter(
            id=attrs["patient_id"],
            user=self.context["request"].user,
            is_active=True,
        ).first()
        if patient is None:
            raise ValidationError({"patient_id": "Pacjent nie istnieje."})

        appointment_type = AppointmentType.objects.filter(
            id=attrs["appointment_type_id"]
        ).first()
        if appointment_type is None:
            raise ValidationError({"appointment_type_id": "Typ wizyty nie istnieje."})

        is_weekly = attrs.get("is_weekly", False)

        if is_weekly and not appointment_type.is_periodic:
            raise ValidationError(
                {"appointment_type_id": "Ten typ wizyty nie obsługuje rezerwacji cyklicznej."}
            )

        start_time = attrs["start_time"]
        end_time = (
            datetime.combine(attrs["start_date"], start_time)
            + timedelta(minutes=appointment_type.duration_time_minutes)
        ).time()
        start_date = attrs["start_date"]

        attrs["therapist"] = therapist
        attrs["patient"] = patient
        attrs["appointment_type"] = appointment_type
        attrs["end_time"] = end_time
        attrs["is_weekly"] = is_weekly

        if not is_weekly:
            self._validate_occurrence(therapist, start_date, start_time, end_time)
            return attrs

        temp_series = AppointmentSeries(
            therapist=therapist,
            patient=attrs["patient"],
            appointment_type=attrs["appointment_type"],
            start_time=start_time,
            end_time=end_time,
            start_date=start_date,
            is_weekly=True,
        )
        horizon_date = AppointmentGenerationEngine.default_horizon_date()
        occurrence_dates = AppointmentGenerationEngine._occurrence_dates(
            temp_series, max(start_date, timezone.localdate()), horizon_date
        )
        if not occurrence_dates:
            raise ValidationError(
                {"is_weekly": "Brak terminów w wybranym okresie rezerwacji."}
            )

        for occurrence_date in occurrence_dates:
            if CollisionDetectionEngine.check(
                therapist.id, occurrence_date, start_time, end_time
            ):
                raise ConflictError()
            if not self._slot_available_without_collision_check(
                therapist, occurrence_date, start_time, end_time
            ):
                raise ValidationError(
                    {"detail": "Wybrany termin jest niedostępny w grafiku terapeuty."}
                )

        self._validate_booking_window(start_date)
        return attrs

    @staticmethod
    def _validate_booking_window(start_date):
        try:
            BookingEngine.validate_booking_date(start_date)
        except Exception as exc:
            raise ValidationError({"start_date": str(exc)}) from exc

    @staticmethod
    def _slot_available_without_collision_check(
        therapist, appointment_date, start_time, end_time
    ):
        return BookingEngine.slot_in_availability(
            therapist, appointment_date, start_time, end_time
        )

    @transaction.atomic
    def create(self, validated_data):
        series = AppointmentSeries.objects.create(
            therapist=validated_data["therapist"],
            patient=validated_data["patient"],
            appointment_type=validated_data["appointment_type"],
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
            start_date=validated_data["start_date"],
            is_weekly=validated_data["is_weekly"],
        )
        AppointmentGenerationEngine.generate(series)
        ensure_horizon(series)
        NotificationEngine.notify_reservation_created(series)
        return series


class AppointmentClientSerializer(serializers.ModelSerializer):
    therapist_name = serializers.CharField(source="therapist.user.get_full_name", read_only=True)
    patient_name = serializers.SerializerMethodField()
    appointment_type_name = serializers.CharField(
        source="appointment_series.appointment_type.name", read_only=True
    )
    start_time = serializers.TimeField(
        source="appointment_series.start_time", read_only=True
    )
    end_time = serializers.TimeField(source="appointment_series.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "appointment_date",
            "status",
            "final_price",
            "therapist_name",
            "patient_name",
            "appointment_type_name",
            "start_time",
            "end_time",
        )

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"


class AppointmentTherapistSerializer(AppointmentClientSerializer):
    class Meta(AppointmentClientSerializer.Meta):
        fields = AppointmentClientSerializer.Meta.fields + ("notes",)


class AppointmentDetailSerializer(AppointmentTherapistSerializer):
    patient_first_name = serializers.CharField(source="patient.first_name", read_only=True)
    patient_last_name = serializers.CharField(source="patient.last_name", read_only=True)
    therapist_first_name = serializers.CharField(
        source="therapist.user.first_name", read_only=True
    )
    therapist_last_name = serializers.CharField(
        source="therapist.user.last_name", read_only=True
    )

    class Meta(AppointmentTherapistSerializer.Meta):
        fields = AppointmentTherapistSerializer.Meta.fields + (
            "patient_first_name",
            "patient_last_name",
            "therapist_first_name",
            "therapist_last_name",
        )


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            Appointment.Status.COMPLETED,
            Appointment.Status.CANCELED,
        ]
    )


class AppointmentNoteSerializer(serializers.Serializer):
    notes = serializers.CharField(allow_blank=True)
