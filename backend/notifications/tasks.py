from datetime import datetime, timedelta

from celery import shared_task
from constance import config
from django.db import transaction
from django.utils import timezone

from notifications.services import NotificationService
from reservations.models import Appointment


@shared_task(name="notifications.tasks.send_appointment_reminders")
def send_appointment_reminders():
    now = timezone.now()
    reminder_delta = timedelta(hours=config.REMINDER_HOURS_BEFORE)
    daily_window = timedelta(hours=24)

    appointments = Appointment.objects.filter(
        status=Appointment.Status.SCHEDULED,
        reminder_sent=False,
    ).select_related("appointment_series")

    for appointment in appointments:
        series = appointment.appointment_series
        start = timezone.make_aware(datetime.combine(appointment.appointment_date, series.start_time))
        remind_at = start - reminder_delta
        if remind_at <= now < remind_at + daily_window:
            with transaction.atomic():
                updated = Appointment.objects.filter(
                    pk=appointment.pk,
                    reminder_sent=False,
                ).update(reminder_sent=True)
                if updated:
                    NotificationService.notify_upcoming_appointment(appointment)
