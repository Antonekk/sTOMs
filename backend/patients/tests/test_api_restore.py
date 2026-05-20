from rest_framework import status

from .base import PatientAPITestCase


class PatientRestoreAPITestCase(PatientAPITestCase):
    def test_restore_soft_deleted_patient(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.post(
            f"/api/v1/patients/{self.child_patient.id}/restore/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_active"])
        self.child_patient.refresh_from_db()
        self.assertTrue(self.child_patient.is_active)

    def test_restore_active_patient_returns_404(self):
        self.authenticate(self.client_user)

        response = self.client.post(
            f"/api/v1/patients/{self.child_patient.id}/restore/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
