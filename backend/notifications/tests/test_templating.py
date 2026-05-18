from django.test import TestCase

from notifications.templating import render_notification


class NotificationTemplateTestCase(TestCase):
    def test_all_notification_templates_render(self):
        base_context = {
            "appointment_type": "Type",
            "start_time": "10:00",
            "appointment_date": "2025-09-01",
            "start_date": "2025-09-01",
            "weekday": "poniedziałek",
            "patient_name": "E F",
            "localization_name": "Loc",
            "room_number": "101",
            "count": 2,
            "dates_display": "2025-09-01, 2025-09-08",
        }
        template_paths = [
            "reservation_created/client_one_time",
            "reservation_created/client_recurring",
            "reservation_created/therapist_one_time",
            "reservation_created/therapist_recurring",
            "appointment_canceled_by_client",
            "appointment_canceled_by_therapist",
            "series_canceled_by_client",
            "appointment_auto_canceled",
            "appointments_bulk_auto_canceled",
            "upcoming_appointment",
        ]
        for template_path in template_paths:
            with self.subTest(template_path=template_path):
                title, description = render_notification(template_path, base_context)
                self.assertTrue(title)
                self.assertTrue(description)
