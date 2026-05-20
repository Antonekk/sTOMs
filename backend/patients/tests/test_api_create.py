from rest_framework import status

from patients.models import Patient

from .base import PatientAPITestCase


class PatientCreateAPITestCase(PatientAPITestCase):
    def test_create_patient(self):
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/v1/patients/",
            {
                "first_name": "F",
                "last_name": "X",
                "birthday": "2020-03-10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "F")
        self.assertEqual(response.data["last_name"], "X")
        self.assertEqual(response.data["birthday"], "2020-03-10")
        self.assertFalse(response.data["is_primary"])
        self.assertTrue(response.data["is_active"])

        patient = Patient.objects.get(first_name="F", last_name="X")
        self.assertEqual(patient.user, self.client_user)
        self.assertFalse(patient.is_primary)

    def test_create_duplicate_patient_returns_readable_error(self):
        self.authenticate(self.client_user)

        payload = {
            "first_name": self.child_patient.first_name,
            "last_name": self.child_patient.last_name,
            "birthday": self.child_patient.date_of_birth.isoformat(),
        }
        response = self.client.post("/api/v1/patients/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("już istnieje", str(response.data))

    def test_create_duplicate_soft_deleted_patient_suggests_restore(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/v1/patients/",
            {
                "first_name": self.child_patient.first_name,
                "last_name": self.child_patient.last_name,
                "birthday": self.child_patient.date_of_birth.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("przywróć", str(response.data))
