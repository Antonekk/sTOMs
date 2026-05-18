from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from patients.models import Patient
from users.serializers import AppUserCreatePasswordRetypeSerializer

from .helpers import PASSWORD

User = get_user_model()


class RegistrationCreatesPatientTestCase(TestCase):
    def test_register_creates_exactly_one_patient_with_birthday(self):
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

        patients = Patient.objects.filter(user=user)
        self.assertEqual(patients.count(), 1)

        patient = patients.get()
        self.assertEqual(patient.first_name, "A")
        self.assertEqual(patient.last_name, "B")
        self.assertEqual(patient.date_of_birth, date(1995, 5, 20))
        self.assertTrue(patient.is_primary)
        self.assertTrue(patient.is_active)
