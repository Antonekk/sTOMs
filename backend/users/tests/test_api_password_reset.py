from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from djoser.utils import encode_uid
from rest_framework import status
from rest_framework.test import APIClient

from .helpers import NEW_PASSWORD, PASSWORD, create_client


class PasswordResetAPITestCase(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = create_client()

    def test_reset_password_request_returns_success(self):
        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            response = self.api.post(
                reverse("user-reset-password"),
                {"email": self.user.email},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reset_password_confirm_changes_password(self):
        uid = encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)

        response = self.api.post(
            reverse("user-reset-password-confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": NEW_PASSWORD,
                "re_new_password": NEW_PASSWORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

    def test_reset_password_confirm_rejects_invalid_token(self):
        uid = encode_uid(self.user.pk)

        response = self.api.post(
            reverse("user-reset-password-confirm"),
            {
                "uid": uid,
                "token": "invalid-token",
                "new_password": NEW_PASSWORD,
                "re_new_password": NEW_PASSWORD,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
