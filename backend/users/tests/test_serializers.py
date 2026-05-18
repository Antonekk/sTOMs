from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from patients.models import Patient

from users.serializers import AppUserCreatePasswordRetypeSerializer, AppUserSerializer

from .helpers import PASSWORD, create_client

User = get_user_model()


class AppUserSerializerTestCase(TestCase):
    def test_register_serializer_rejects_phone_without_plus48_prefix(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "r@test.com",
                "phone_number": "123456789",
                "first_name": "A",
                "last_name": "B",
                "password": PASSWORD,
                "re_password": PASSWORD,
                "date_of_birth": date(1995, 5, 20),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_register_serializer_creates_primary_patient(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "r@test.com",
                "phone_number": "+48111111111",
                "first_name": "A",
                "last_name": "B",
                "password": PASSWORD,
                "re_password": PASSWORD,
                "date_of_birth": date(1995, 5, 20),
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        patient = Patient.objects.get(user=user)
        self.assertEqual(patient.first_name, "A")
        self.assertEqual(patient.last_name, "B")
        self.assertEqual(patient.date_of_birth, date(1995, 5, 20))
        self.assertTrue(patient.is_primary)

    def test_register_serializer_rejects_underage_primary_patient(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "r2@test.com",
                "phone_number": "+48111111112",
                "first_name": "A",
                "last_name": "B",
                "password": PASSWORD,
                "re_password": PASSWORD,
                "date_of_birth": date.today(),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)

    def test_user_serializer_exposes_role_and_patients(self):
        user = create_client()
        Patient.objects.create(
            user=user,
            first_name="A",
            last_name="B",
            date_of_birth=date(1995, 5, 20),
            is_primary=True,
        )

        data = AppUserSerializer(instance=user).data

        self.assertEqual(data["role"], User.Role.CLIENT)
        self.assertEqual(len(data["patients"]), 1)
        self.assertEqual(data["patients"][0]["first_name"], "A")
