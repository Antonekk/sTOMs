from datetime import datetime, timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from notifications.engine import NotificationEngine
from patients.models import Patient
from therapist_availability.models import Therapist

from .models import Appointment, AppointmentSeries, AppointmentType
from .engines.booking import BookingEngine
from .engines.collision import CollisionDetectionEngine
from .engines.generation import AppointmentGenerationEngine
from .engines.horizon import HorizonEngine
from offices.location import serialize_office_location

WEEKDAY_LABELS = [
    "poniedziałek",
    "wtorek",
    "środa",
    "czwartek",
    "piątek",
    "sobota",
    "niedziela",
]


class PatientOfficeMixin(serializers.Serializer):
    patient_name = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_office(self, obj):
        return serialize_office_location(obj.therapist.office)


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


class AppointmentSeriesListSerializer(PatientOfficeMixin, serializers.ModelSerializer):
    therapist_name = serializers.CharField(source="therapist.user.get_full_name", read_only=True)
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
            "office",
        )

    @extend_schema_field(serializers.CharField(allow_null=True))
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

    @staticmethod
    def _raise_validation_from_booking_error(exc):
        message = str(exc.message or exc)
        if "zajęty" in message or "koliduje" in message:
            raise ValidationError(
                {"detail": "Wybrany termin koliduje z istniejącą wizytą."}
            ) from exc
        if hasattr(exc, "message_dict"):
            raise ValidationError(exc.message_dict) from exc
        raise ValidationError({"detail": message}) from exc

    def _validate_occurrence(self, therapist, occurrence_date, start_time, end_time):
        try:
            BookingEngine.validate_slot(therapist, occurrence_date, start_time, end_time)
        except DjangoValidationError as exc:
            self._raise_validation_from_booking_error(exc)

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
        start_date = attrs["start_date"]
        end_time = (
            datetime.combine(start_date, start_time)
            + timedelta(minutes=appointment_type.duration_time_minutes)
        ).time()

        attrs.update(
            {
                "therapist": therapist,
                "patient": patient,
                "appointment_type": appointment_type,
                "end_time": end_time,
                "is_weekly": is_weekly,
            }
        )

        try:
            BookingEngine.validate_booking_date(start_date)
        except Exception as exc:
            raise ValidationError({"start_date": str(exc)}) from exc

        if not is_weekly:
            self._validate_occurrence(therapist, start_date, start_time, end_time)
            return attrs

        temp_series = AppointmentSeries(
            therapist=therapist,
            patient=patient,
            appointment_type=appointment_type,
            start_time=start_time,
            end_time=end_time,
            start_date=start_date,
            is_weekly=True,
        )
        horizon_date = HorizonEngine.default_horizon_date()
        occurrence_dates = AppointmentGenerationEngine._occurrence_dates(
            temp_series, max(start_date, timezone.localdate()), horizon_date
        )
        if not occurrence_dates:
            raise ValidationError(
                {"is_weekly": "Brak terminów w wybranym okresie rezerwacji."}
            )

        if CollisionDetectionEngine.has_active_weekly_series_conflict(
            therapist.id, start_date.weekday(), start_time, end_time
        ):
            raise ValidationError(
                {"detail": "Wybrany termin koliduje z istniejącą wizytą."}
            )

        for occurrence_date in occurrence_dates:
            if CollisionDetectionEngine.check(
                therapist.id, occurrence_date, start_time, end_time
            ):
                raise ValidationError(
                    {"detail": "Wybrany termin koliduje z istniejącą wizytą."}
                )
            if not BookingEngine.slot_in_availability(
                therapist, occurrence_date, start_time, end_time
            ):
                raise ValidationError(
                    {"detail": "Wybrany termin jest niedostępny w grafiku terapeuty."}
                )

        return attrs

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
        NotificationEngine.notify_reservation_created(series)
        return series


class AppointmentClientSerializer(PatientOfficeMixin, serializers.ModelSerializer):
    therapist_name = serializers.CharField(source="therapist.user.get_full_name", read_only=True)
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
            "office",
        )


class AppointmentTherapistSerializer(AppointmentClientSerializer):
    class Meta(AppointmentClientSerializer.Meta):
        fields = AppointmentClientSerializer.Meta.fields + ("notes",)


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            Appointment.Status.COMPLETED,
            Appointment.Status.CANCELED,
        ]
    )


class AppointmentNoteSerializer(serializers.Serializer):
    notes = serializers.CharField(allow_blank=True)


class BookableSlotSerializer(serializers.Serializer):
    therapist_id = serializers.UUIDField()
    therapist_name = serializers.CharField()
    office_id = serializers.UUIDField(allow_null=True)
    office = serializers.JSONField(allow_null=True)
    date = serializers.DateField()
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")


class BookableTimeOptionsSerializer(serializers.Serializer):
    start_times = serializers.ListField(child=serializers.CharField())
    end_times = serializers.ListField(child=serializers.CharField())


class BookingTherapistSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    office_id = serializers.UUIDField(source="office.id", read_only=True, allow_null=True)
    office = serializers.SerializerMethodField()

    class Meta:
        model = Therapist
        fields = ("id", "full_name", "office_id", "office")

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_office(self, obj):
        return serialize_office_location(obj.office)
