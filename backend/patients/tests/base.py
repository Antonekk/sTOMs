from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .helpers import create_client, create_patient

User = get_user_model()


class PatientAPITestCase(APITestCase):
    def setUp(self):
        self.client_user = create_client()
        self.other_client = create_client(email="c2@test.com")
        self.therapist = create_client(
            email="t@test.com",
            role=User.Role.THERAPIST,
        )
        self.primary_patient = create_patient(
            self.client_user,
            first_name="A",
            last_name="X",
            date_of_birth=date(1990, 1, 1),
            is_primary=True,
        )
        self.child_patient = create_patient(
            self.client_user,
            first_name="B",
            last_name="X",
            date_of_birth=date(2018, 4, 15),
        )
        self.other_patient = create_patient(self.other_client, is_primary=True)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)
