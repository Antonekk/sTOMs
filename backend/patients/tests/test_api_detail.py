from datetime import date

from rest_framework import status

from patients.models import Patient

from .base import PatientAPITestCase


class PatientDetailAPITestCase(PatientAPITestCase):
    def test_retrieve_own_patient(self):
        self.authenticate(self.client_user)

        response = self.client.get(f"/api/v1/patients/{self.child_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "B")
        self.assertEqual(response.data["birthday"], "2018-04-15")

    def test_client_cannot_access_other_clients_patient(self):
        self.authenticate(self.client_user)

        for method, url, data in [
            ("get", f"/api/v1/patients/{self.other_patient.id}/", None),
            (
                "put",
                f"/api/v1/patients/{self.other_patient.id}/",
                {
                    "first_name": "Z",
                    "last_name": "X",
                    "birthday": "2000-01-01",
                },
            ),
            ("delete", f"/api/v1/patients/{self.other_patient.id}/", None),
        ]:
            if method == "get":
                response = self.client.get(url)
            elif method == "put":
                response = self.client.put(url, data, format="json")
            else:
                response = self.client.delete(url)

            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                msg=f"{method.upper()} should return 404",
            )

    def test_update_own_patient(self):
        self.authenticate(self.client_user)

        response = self.client.put(
            f"/api/v1/patients/{self.child_patient.id}/",
            {
                "first_name": "G",
                "last_name": "X",
                "birthday": "2018-04-16",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child_patient.refresh_from_db()
        self.assertEqual(self.child_patient.first_name, "G")
        self.assertEqual(self.child_patient.date_of_birth, date(2018, 4, 16))

    def test_soft_delete_sets_inactive(self):
        self.authenticate(self.client_user)

        response = self.client.delete(f"/api/v1/patients/{self.child_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.child_patient.refresh_from_db()
        self.assertFalse(self.child_patient.is_active)
        self.assertTrue(Patient.objects.filter(id=self.child_patient.id).exists())

    def test_soft_deleted_patient_returns_404_on_detail(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.get(f"/api/v1/patients/{self.child_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_primary_patient(self):
        self.authenticate(self.client_user)

        response = self.client.delete(f"/api/v1/patients/{self.primary_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.primary_patient.refresh_from_db()
        self.assertTrue(self.primary_patient.is_active)

    def test_therapist_cannot_access_patients_endpoint(self):
        self.authenticate(self.therapist)

        response = self.client.get("/api/v1/patients/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
