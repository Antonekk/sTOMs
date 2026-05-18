from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .helpers import create_client, create_therapist

User = get_user_model()


class AppUserModelTestCase(TestCase):
    def test_phone_number_requires_plus48_prefix(self):
        user = User(
            email="p@test.com",
            phone_number="123456789",
            first_name="A",
            last_name="B",
        )

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_role_helpers_and_full_name(self):
        client = create_client()
        therapist = create_therapist()

        self.assertEqual(str(client), "c@test.com")
        self.assertEqual(client.get_full_name(), "A B")
        self.assertEqual(therapist.get_full_name(), "C D")
        self.assertTrue(client.is_client)
        self.assertFalse(client.is_therapist)
        self.assertTrue(therapist.is_therapist)
        self.assertFalse(therapist.is_client)
