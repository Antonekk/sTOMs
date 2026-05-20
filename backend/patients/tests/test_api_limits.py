from datetime import date

from constance import config
from rest_framework import status

from patients.models import Patient

from .base import PatientAPITestCase
from .helpers import create_patient


class PatientLimitAPITestCase(PatientAPITestCase):
    def test_create_rejected_at_max_patients_per_client(self):
        extra_needed = config.MAX_PATIENTS_PER_CLIENT - 2
        for index in range(extra_needed):
            create_patient(
                self.client_user,
                first_name=chr(ord("C") + index),
                last_name="X",
                date_of_birth=date(2017, 2, 1 + index),
            )
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/v1/patients/",
            {
                "first_name": "K",
                "last_name": "X",
                "birthday": "2020-03-10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Patient.objects.filter(
                user=self.client_user,
                first_name="K",
                last_name="X",
                is_active=True,
            ).exists()
        )

    def test_soft_deleted_patients_do_not_count_toward_limit(self):
        for index in range(config.MAX_PATIENTS_PER_CLIENT - 2):
            create_patient(
                self.client_user,
                first_name=chr(ord("C") + index),
                last_name="X",
                date_of_birth=date(2016, 3, 1 + index),
            )
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/v1/patients/",
            {
                "first_name": "L",
                "last_name": "X",
                "birthday": "2021-05-05",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_restore_blocked_when_patient_limit_reached(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        extra_slots = config.MAX_PATIENTS_PER_CLIENT - 1
        for index in range(extra_slots):
            create_patient(
                self.client_user,
                first_name=chr(ord("C") + index),
                last_name="X",
                date_of_birth=date(2016, 1, 1 + index),
            )
        self.authenticate(self.client_user)

        response = self.client.post(
            f"/api/v1/patients/{self.child_patient.id}/restore/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.child_patient.refresh_from_db()
        self.assertFalse(self.child_patient.is_active)
