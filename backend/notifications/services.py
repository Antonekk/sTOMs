from __future__ import annotations

from collections.abc import Iterable

from django.contrib.auth import get_user_model
from django.db import transaction

from notifications.models import Notification
from notifications.templating import (
    format_bulk_dates,
    format_date,
    format_time,
    render_notification,
    weekday_label,
)
from reservations.models import Appointment, AppointmentSeries

User = get_user_model()


class CanceledBy:
    CLIENT = User.Role.CLIENT
    THERAPIST = User.Role.THERAPIST


class NotificationService:
    @classmethod
    def _patient_full_name(cls, series: AppointmentSeries) -> str:
        return f"{series.patient.first_name} {series.patient.last_name}"

    @classmethod
    def _create(cls, user, title: str, description: str) -> Notification:
        return Notification.objects.create(user=user, title=title, description=description)

    @classmethod
    @transaction.atomic
    def notify_reservation_created(cls, series: AppointmentSeries) -> None:
        series = (
            AppointmentSeries.objects.select_related(
                "patient__user",
                "therapist__user",
                "appointment_type",
            )
            .prefetch_related("appointments")
            .get(pk=series.pk)
        )
        appointment_type = series.appointment_type.name
        start_time = format_time(series.start_time)
        patient_name = cls._patient_full_name(series)

        if series.is_recurring:
            context = {
                "appointment_type": appointment_type,
                "start_time": start_time,
                "weekday": weekday_label(series.start_date),
                "start_date": format_date(series.start_date),
                "patient_name": patient_name,
            }
            client_title, client_description = render_notification(
                "reservation_created/client_recurring",
                context,
            )
            therapist_title, therapist_description = render_notification(
                "reservation_created/therapist_recurring",
                context,
            )
        else:
            first_appointment = series.appointments.order_by("appointment_date").first()
            appointment_date = format_date(
                first_appointment.appointment_date if first_appointment else series.start_date
            )
            context = {
                "appointment_type": appointment_type,
                "start_time": start_time,
                "appointment_date": appointment_date,
                "patient_name": patient_name,
            }
            client_title, client_description = render_notification(
                "reservation_created/client_one_time",
                context,
            )
            therapist_title, therapist_description = render_notification(
                "reservation_created/therapist_one_time",
                context,
            )

        cls._create(series.patient.user, client_title, client_description)
        cls._create(series.therapist.user, therapist_title, therapist_description)

    @classmethod
    @transaction.atomic
    def notify_appointment_canceled(cls, appointment: Appointment, canceled_by: str) -> None:
        appointment = Appointment.objects.select_related(
            "patient__user",
            "therapist__user",
            "appointment_series__appointment_type",
            "appointment_series__patient",
        ).get(pk=appointment.pk)
        series = appointment.appointment_series
        context = {
            "appointment_type": series.appointment_type.name,
            "appointment_date": format_date(appointment.appointment_date),
            "start_time": format_time(series.start_time),
            "patient_name": cls._patient_full_name(series),
        }

        if canceled_by == CanceledBy.CLIENT:
            title, description = render_notification(
                "appointment_canceled_by_client",
                context,
            )
            cls._create(series.therapist.user, title, description)
        elif canceled_by == CanceledBy.THERAPIST:
            title, description = render_notification(
                "appointment_canceled_by_therapist",
                context,
            )
            cls._create(series.patient.user, title, description)

    @classmethod
    @transaction.atomic
    def notify_series_canceled(cls, series: AppointmentSeries, canceled_by: str) -> None:
        series = AppointmentSeries.objects.select_related(
            "patient__user",
            "therapist__user",
            "appointment_type",
        ).get(pk=series.pk)

        if canceled_by != CanceledBy.CLIENT:
            return

        context = {
            "appointment_type": series.appointment_type.name,
            "start_date": format_date(series.start_date),
            "weekday": weekday_label(series.start_date),
            "patient_name": cls._patient_full_name(series),
        }
        title, description = render_notification("series_canceled_by_client", context)
        cls._create(series.therapist.user, title, description)

    @classmethod
    @transaction.atomic
    def notify_appointments_canceled_bulk(
        cls,
        appointments: Iterable[Appointment],
        therapist,
    ) -> None:
        appointment_list = list(appointments)
        if not appointment_list:
            return

        for appointment in appointment_list:
            appointment = Appointment.objects.select_related(
                "patient__user",
                "appointment_series__appointment_type",
            ).get(pk=appointment.pk)
            series = appointment.appointment_series
            context = {
                "appointment_type": series.appointment_type.name,
                "appointment_date": format_date(appointment.appointment_date),
                "start_time": format_time(series.start_time),
            }
            title, description = render_notification("appointment_auto_canceled", context)
            cls._create(appointment.patient.user, title, description)

        dates = [appointment.appointment_date for appointment in appointment_list]
        bulk_context = {
            "count": len(appointment_list),
            "dates_display": format_bulk_dates(dates),
        }
        title, description = render_notification(
            "appointments_bulk_auto_canceled",
            bulk_context,
        )
        cls._create(therapist.user, title, description)

    @classmethod
    @transaction.atomic
    def notify_upcoming_appointment(cls, appointment: Appointment) -> None:
        appointment = Appointment.objects.select_related(
            "patient__user",
            "appointment_series__appointment_type",
            "therapist__office__localization",
        ).get(pk=appointment.pk)
        series = appointment.appointment_series
        office = appointment.therapist.office
        context = {
            "appointment_type": series.appointment_type.name,
            "start_time": format_time(series.start_time),
            "localization_name": office.localization.name if office else "—",
            "room_number": office.room_number if office and office.room_number else "—",
        }
        title, description = render_notification("upcoming_appointment", context)
        cls._create(appointment.patient.user, title, description)
