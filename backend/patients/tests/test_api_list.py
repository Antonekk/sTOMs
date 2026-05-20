from datetime import date

from rest_framework import status

from .base import PatientAPITestCase
from .helpers import create_patient


class PatientListAPITestCase(PatientAPITestCase):
    def test_list_returns_only_active_patients_for_client(self):
        inactive = create_patient(
            self.client_user,
            first_name="C",
            last_name="X",
            date_of_birth=date(2015, 6, 1),
            is_active=False,
        )
        self.authenticate(self.client_user)

        response = self.client.get("/api/v1/patients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        patients_by_id = {item["id"]: item for item in response.data}
        self.assertTrue(patients_by_id[str(self.primary_patient.id)]["is_primary"])
        self.assertFalse(patients_by_id[str(self.child_patient.id)]["is_primary"])
        returned_ids = set(patients_by_id.keys())
        self.assertIn(str(self.primary_patient.id), returned_ids)
        self.assertIn(str(self.child_patient.id), returned_ids)
        self.assertNotIn(str(inactive.id), returned_ids)

    def test_list_inactive_returns_only_soft_deleted_patients(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        inactive = create_patient(
            self.client_user,
            first_name="D",
            last_name="X",
            date_of_birth=date(2015, 6, 1),
            is_active=False,
        )
        self.authenticate(self.client_user)

        response = self.client.get("/api/v1/patients/", {"is_active": "false"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        returned_ids = {item["id"] for item in response.data}
        self.assertIn(str(self.child_patient.id), returned_ids)
        self.assertIn(str(inactive.id), returned_ids)
        self.assertNotIn(str(self.primary_patient.id), returned_ids)
        for item in response.data:
            self.assertFalse(item["is_active"])
