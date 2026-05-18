from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import Notification

from .helpers import create_client, create_therapist


class NotificationAPITestCase(APITestCase):
    def setUp(self):
        self.therapist_user, self.therapist = create_therapist()
        self.client_user, self.patient = create_client()
        self.other_user, _ = create_client("c2@test.com")
        self.api = APIClient()

        self.client_notification = Notification.objects.create(
            user=self.client_user,
            title="T1",
            description="D1",
        )
        self.other_notification = Notification.objects.create(
            user=self.other_user,
            title="T2",
            description="D2",
        )

    def test_list_returns_only_own_notifications(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get("/api/v1/notifications")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.client_notification.id))

    def test_mark_read_other_user_notification_returns_404(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/notifications/{self.other_notification.id}/read"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_notification.refresh_from_db()
        self.assertFalse(self.other_notification.is_read)

    def test_mark_all_read_updates_only_authenticated_user_notifications(self):
        Notification.objects.create(
            user=self.client_user,
            title="T3",
            description="D3",
            is_read=False,
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch("/api/v1/notifications/read")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Notification.objects.filter(user=self.client_user, is_read=False).exists()
        )
        self.other_notification.refresh_from_db()
        self.assertFalse(self.other_notification.is_read)

    def test_mark_single_notification_as_read(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.patch(
            f"/api/v1/notifications/{self.client_notification.id}/read"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_notification.refresh_from_db()
        self.assertTrue(self.client_notification.is_read)
