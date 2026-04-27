from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from patients.cache_utils import (
    get_cached_patient_detail,
    get_cached_patient_list,
)
from constance import config
from patients.models import Patient
from rest_framework import status
from rest_framework.test import APITestCase

from users.serializers import AppUserCreatePasswordRetypeSerializer

User = get_user_model()


def create_client(email="client@test.com", **extra_fields):
    defaults = {
        "password": "Bezpieczne#123",
        "phone_number": "+48123456789",
        "first_name": "Jan",
        "last_name": "Kowalski",
        "role": User.Role.CLIENT,
    }
    defaults.update(extra_fields)
    return User.objects.create_user(email=email, **defaults)


def create_patient(user, **extra_fields):
    defaults = {
        "first_name": "Anna",
        "last_name": "Nowak",
        "date_of_birth": date(2018, 4, 15),
        "is_primary": False,
        "is_active": True,
    }
    defaults.update(extra_fields)
    return Patient.objects.create(user=user, **defaults)


class TestRegistrationCreatesPatient(TestCase):
    def test_register_creates_exactly_one_patient_with_birthday(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "anna@example.com",
                "phone_number": "+48123456789",
                "first_name": "Anna",
                "last_name": "Kowalska",
                "password": "Bezpieczne#123",
                "re_password": "Bezpieczne#123",
                "date_of_birth": date(1995, 5, 20),
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        patients = Patient.objects.filter(user=user)
        self.assertEqual(patients.count(), 1)

        patient = patients.get()
        self.assertEqual(patient.first_name, "Anna")
        self.assertEqual(patient.last_name, "Kowalska")
        self.assertEqual(patient.date_of_birth, date(1995, 5, 20))
        self.assertTrue(patient.is_primary)
        self.assertTrue(patient.is_active)


class TestPatientAPI(APITestCase):
    def setUp(self):
        self.client_user = create_client()
        self.other_client = create_client(
            email="other@test.com",
            phone_number="+48222222222",
        )
        self.therapist = create_client(
            email="therapist@test.com",
            phone_number="+48333333333",
            role=User.Role.THERAPIST,
        )
        self.primary_patient = create_patient(
            self.client_user,
            first_name="Jan",
            last_name="Kowalski",
            date_of_birth=date(1990, 1, 1),
            is_primary=True,
        )
        self.child_patient = create_patient(
            self.client_user,
            first_name="Tomasz",
            last_name="Kowalski",
            date_of_birth=date(2018, 4, 15),
        )
        self.other_patient = create_patient(self.other_client, is_primary=True)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_list_returns_only_active_patients_for_client(self):
        inactive = create_patient(
            self.client_user,
            first_name="Inactive",
            last_name="Patient",
            date_of_birth=date(2015, 6, 1),
            is_active=False,
        )
        self.authenticate(self.client_user)

        response = self.client.get("/api/patients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        patients_by_id = {item["id"]: item for item in response.data}
        self.assertTrue(patients_by_id[str(self.primary_patient.id)]["is_primary"])
        self.assertFalse(patients_by_id[str(self.child_patient.id)]["is_primary"])
        returned_ids = set(patients_by_id.keys())
        self.assertIn(str(self.primary_patient.id), returned_ids)
        self.assertIn(str(self.child_patient.id), returned_ids)
        self.assertNotIn(str(inactive.id), returned_ids)

    def test_create_patient(self):
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/patients/",
            {
                "first_name": "Maria",
                "last_name": "Kowalski",
                "birthday": "2020-03-10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Maria")
        self.assertEqual(response.data["last_name"], "Kowalski")
        self.assertEqual(response.data["birthday"], "2020-03-10")
        self.assertFalse(response.data["is_primary"])
        self.assertTrue(response.data["is_active"])

        patient = Patient.objects.get(first_name="Maria", last_name="Kowalski")
        self.assertEqual(patient.user, self.client_user)
        self.assertFalse(patient.is_primary)

    def test_create_duplicate_patient_returns_readable_error(self):
        self.authenticate(self.client_user)

        payload = {
            "first_name": self.child_patient.first_name,
            "last_name": self.child_patient.last_name,
            "birthday": self.child_patient.date_of_birth.isoformat(),
        }
        response = self.client.post("/api/patients/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "już istnieje",
            str(response.data),
        )

    def test_create_duplicate_soft_deleted_patient_suggests_restore(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/patients/",
            {
                "first_name": self.child_patient.first_name,
                "last_name": self.child_patient.last_name,
                "birthday": self.child_patient.date_of_birth.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Przywróć", str(response.data))

    def test_retrieve_own_patient(self):
        self.authenticate(self.client_user)

        response = self.client.get(f"/api/patients/{self.child_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Tomasz")
        self.assertEqual(response.data["birthday"], "2018-04-15")

    def test_client_cannot_access_other_clients_patient(self):
        self.authenticate(self.client_user)

        for method, url, data in [
            ("get", f"/api/patients/{self.other_patient.id}/", None),
            (
                "put",
                f"/api/patients/{self.other_patient.id}/",
                {
                    "first_name": "Hacked",
                    "last_name": "Name",
                    "birthday": "2000-01-01",
                },
            ),
            ("delete", f"/api/patients/{self.other_patient.id}/", None),
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
            f"/api/patients/{self.child_patient.id}/",
            {
                "first_name": "Tomek",
                "last_name": "Kowalski",
                "birthday": "2018-04-16",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.child_patient.refresh_from_db()
        self.assertEqual(self.child_patient.first_name, "Tomek")
        self.assertEqual(self.child_patient.date_of_birth, date(2018, 4, 16))

    def test_soft_delete_hides_patient_from_list(self):
        self.authenticate(self.client_user)

        response = self.client.delete(f"/api/patients/{self.child_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.child_patient.refresh_from_db()
        self.assertFalse(self.child_patient.is_active)
        self.assertTrue(Patient.objects.filter(id=self.child_patient.id).exists())

        list_response = self.client.get("/api/patients/")
        returned_ids = {item["id"] for item in list_response.data}
        self.assertNotIn(str(self.child_patient.id), returned_ids)

    def test_soft_deleted_patient_returns_404_on_detail(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.get(f"/api/patients/{self.child_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_primary_patient(self):
        self.authenticate(self.client_user)

        response = self.client.delete(f"/api/patients/{self.primary_patient.id}/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.primary_patient.refresh_from_db()
        self.assertTrue(self.primary_patient.is_active)

    def test_therapist_cannot_access_patients_endpoint(self):
        self.authenticate(self.therapist)

        response = self.client.get("/api/patients/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_restore_soft_deleted_patient(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.post(
            f"/api/patients/{self.child_patient.id}/restore/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_active"])
        self.child_patient.refresh_from_db()
        self.assertTrue(self.child_patient.is_active)

        list_response = self.client.get("/api/patients/")
        returned_ids = {item["id"] for item in list_response.data}
        self.assertIn(str(self.child_patient.id), returned_ids)

    def test_restore_active_patient_returns_404(self):
        self.authenticate(self.client_user)

        response = self.client.post(
            f"/api/patients/{self.child_patient.id}/restore/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_restore_blocked_when_patient_limit_reached(self):
        self.child_patient.is_active = False
        self.child_patient.save()
        extra_slots = config.MAX_PATIENTS_PER_CLIENT - 1
        for index in range(extra_slots):
            create_patient(
                self.client_user,
                first_name=f"Extra{index}",
                last_name="Pacjent",
                date_of_birth=date(2016, 1, 1 + index),
            )
        self.authenticate(self.client_user)

        response = self.client.post(
            f"/api/patients/{self.child_patient.id}/restore/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.child_patient.refresh_from_db()
        self.assertFalse(self.child_patient.is_active)

    def test_create_rejected_at_max_patients_per_client(self):
        extra_needed = config.MAX_PATIENTS_PER_CLIENT - 2
        for index in range(extra_needed):
            create_patient(
                self.client_user,
                first_name=f"Child{index}",
                last_name="Kowalski",
                date_of_birth=date(2017, 2, 1 + index),
            )
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/patients/",
            {
                "first_name": "Maria",
                "last_name": "Kowalski",
                "birthday": "2020-03-10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Patient.objects.filter(
                user=self.client_user,
                first_name="Maria",
                last_name="Kowalski",
                is_active=True,
            ).exists()
        )

    def test_soft_deleted_patients_do_not_count_toward_limit(self):
        for index in range(config.MAX_PATIENTS_PER_CLIENT - 2):
            create_patient(
                self.client_user,
                first_name=f"Slot{index}",
                last_name="Kowalski",
                date_of_birth=date(2016, 3, 1 + index),
            )
        self.child_patient.is_active = False
        self.child_patient.save()
        self.authenticate(self.client_user)

        response = self.client.post(
            "/api/patients/",
            {
                "first_name": "Zofia",
                "last_name": "Kowalski",
                "birthday": "2021-05-05",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_response_is_cached(self):
        cache.clear()
        self.authenticate(self.client_user)

        self.client.get("/api/patients/")
        cached = get_cached_patient_list(self.client_user.id)
        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 2)

    def test_list_cache_invalidated_after_create(self):
        cache.clear()
        self.authenticate(self.client_user)
        self.client.get("/api/patients/")
        self.assertIsNotNone(get_cached_patient_list(self.client_user.id))

        self.client.post(
            "/api/patients/",
            {
                "first_name": "Ewa",
                "last_name": "Kowalski",
                "birthday": "2019-08-12",
            },
            format="json",
        )

        self.assertIsNone(get_cached_patient_list(self.client_user.id))

    def test_retrieve_response_is_cached(self):
        cache.clear()
        self.authenticate(self.client_user)

        self.client.get(f"/api/patients/{self.child_patient.id}/")
        cached = get_cached_patient_detail(
            self.client_user.id, self.child_patient.id
        )
        self.assertIsNotNone(cached)
        self.assertEqual(cached["first_name"], "Tomasz")

    def test_detail_cache_invalidated_after_update(self):
        cache.clear()
        self.authenticate(self.client_user)
        self.client.get(f"/api/patients/{self.child_patient.id}/")
        self.assertIsNotNone(
            get_cached_patient_detail(
                self.client_user.id, self.child_patient.id
            )
        )

        self.client.put(
            f"/api/patients/{self.child_patient.id}/",
            {
                "first_name": "Tomek",
                "last_name": "Kowalski",
                "birthday": "2018-04-15",
            },
            format="json",
        )

        self.assertIsNone(
            get_cached_patient_detail(
                self.client_user.id, self.child_patient.id
            )
        )


@override_settings(
    REST_FRAMEWORK={
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            **settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
            "patients": "3/minute",
        },
    }
)
class TestPatientEndpointThrottling(APITestCase):
    def setUp(self):
        cache.clear()
        self.client_user = create_client()
        create_patient(self.client_user, is_primary=True)
        self.authenticate(self.client_user)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_patients_list_is_throttled(self):
        url = "/api/patients/"

        for _ in range(3):
            response = self.client.get(url)
            self.assertNotEqual(
                response.status_code, status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
