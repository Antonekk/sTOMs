from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from djoser.utils import encode_uid
from rest_framework import status
from rest_framework.test import APIClient

from .helpers import create_client


class AccountActivationAPITestCase(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = create_client()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.uid = encode_uid(self.user.pk)
        self.token = default_token_generator.make_token(self.user)

    def test_activation_activates_user_and_sends_confirmation_once(self):
        url = reverse("user-activation")
        payload = {"uid": self.uid, "token": self.token}

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            response = self.api.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(len(mail.outbox), 1)

            response = self.api.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(len(mail.outbox), 1)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activation_rejects_invalid_token(self):
        response = self.api.post(
            reverse("user-activation"),
            {"uid": self.uid, "token": "invalid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
