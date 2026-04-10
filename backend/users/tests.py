from datetime import date
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from patients.models import Patient
from rest_framework.test import APIRequestFactory

from .permissions import (
    IsAdminUser,
    IsClient,
    IsTherapist,
    PatientPermissions,
    TherapistPermissions,
)
from .serializers import AppUserCreatePasswordRetypeSerializer, AppUserSerializer


User = get_user_model()


def create_user(email="test@test.com", phone_number="+48123456789", **extra_fields):
    defaults = {
        "password": "Bezpieczne#123",
        "first_name": "Jan",
        "last_name": "Kowalski",
    }
    defaults.update(extra_fields)
    return User.objects.create_user(
        email=email,
        phone_number=phone_number,
        **defaults,
    )


class TestUserManagers(TestCase):
    def test_create_user(self):
        user = create_user()

        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.phone_number, "+48123456789")
        self.assertTrue(user.check_password("Bezpieczne#123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, User.Role.CLIENT)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="test@test.com")
        with self.assertRaises(TypeError):
            User.objects.create_user(email="", phone_number="+48123456789")

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email="admin@test.com",
            phone_number="+48987654321",
            password="foo",
            first_name="Admin",
            last_name="User",
        )

        self.assertEqual(admin_user.email, "admin@test.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, User.Role.ADMIN)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin2@test.com",
                phone_number="+48111111111",
                password="foo",
                is_staff=False,
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin3@test.com",
                phone_number="+48222222222",
                password="foo",
                is_superuser=False,
            )


class TestAppUserModel(TestCase):
    def test_role_helpers_and_full_name(self):
        client = create_user(first_name="Anna", last_name="Nowak")
        therapist = create_user(
            email="therapist@test.com",
            phone_number="+48111111111",
            role=User.Role.THERAPIST,
        )

        self.assertEqual(str(client), "test@test.com")
        self.assertEqual(client.get_full_name(), "Anna Nowak")
        self.assertTrue(client.is_client)
        self.assertFalse(client.is_therapist)
        self.assertTrue(therapist.is_therapist)
        self.assertFalse(therapist.is_client)


class TestAppUserSerializers(TestCase):
    def test_register_serializer_creates_primary_patient(self):
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

        patient = Patient.objects.get(user=user)
        self.assertEqual(patient.first_name, "Anna")
        self.assertEqual(patient.last_name, "Kowalska")
        self.assertEqual(patient.date_of_birth, date(1995, 5, 20))
        self.assertTrue(patient.is_primary)

    def test_register_serializer_rejects_underage_primary_patient(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "child@example.com",
                "phone_number": "+48123456789",
                "first_name": "Jan",
                "last_name": "Kowalski",
                "password": "Bezpieczne#123",
                "re_password": "Bezpieczne#123",
                "date_of_birth": date.today(),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)

    def test_user_serializer_exposes_role_and_patients(self):
        user = create_user(first_name="Anna", last_name="Nowak")
        Patient.objects.create(
            user=user,
            first_name="Anna",
            last_name="Nowak",
            date_of_birth=date(1995, 5, 20),
            is_primary=True,
        )

        data = AppUserSerializer(instance=user).data

        self.assertEqual(data["role"], User.Role.CLIENT)
        self.assertEqual(len(data["patients"]), 1)
        self.assertEqual(data["patients"][0]["first_name"], "Anna")


class TestUserPermissions(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client_user = create_user(
            email="client@test.com",
            phone_number="+48111111111",
            role=User.Role.CLIENT,
        )
        self.other_client = create_user(
            email="other-client@test.com",
            phone_number="+48222222222",
            role=User.Role.CLIENT,
        )
        self.therapist = create_user(
            email="therapist@test.com",
            phone_number="+48333333333",
            role=User.Role.THERAPIST,
        )
        self.admin = create_user(
            email="admin@test.com",
            phone_number="+48444444444",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.patient = Patient.objects.create(
            user=self.client_user,
            first_name="Anna",
            last_name="Nowak",
            date_of_birth=date(1995, 5, 20),
            is_primary=True,
        )

    def request(self, method, user):
        request = getattr(self.factory, method.lower())("/")
        request.user = user
        return request

    def test_patient_permissions_allow_client_full_access_to_own_patient(self):
        permission = PatientPermissions()

        request = self.request("GET", self.client_user)
        self.assertTrue(permission.has_permission(request, None))
        self.assertTrue(permission.has_object_permission(request, None, self.patient))

        request = self.request("DELETE", self.client_user)
        self.assertTrue(permission.has_permission(request, None))
        self.assertTrue(permission.has_object_permission(request, None, self.patient))

    def test_patient_permissions_deny_client_access_to_other_patient(self):
        permission = PatientPermissions()
        request = self.request("GET", self.other_client)

        self.assertTrue(permission.has_permission(request, None))
        self.assertFalse(permission.has_object_permission(request, None, self.patient))

    def test_patient_permissions_limit_therapist_to_safe_methods(self):
        permission = PatientPermissions()

        request = self.request("GET", self.therapist)
        self.assertTrue(permission.has_permission(request, None))
        self.assertTrue(permission.has_object_permission(request, None, self.patient))

        request = self.request("POST", self.therapist)
        self.assertFalse(permission.has_permission(request, None))
        self.assertFalse(permission.has_object_permission(request, None, self.patient))

    def test_patient_permissions_deny_anonymous_user(self):
        permission = PatientPermissions()
        request = self.request("GET", AnonymousUser())

        self.assertFalse(permission.has_permission(request, None))

    def test_role_permissions(self):
        view = SimpleNamespace()

        self.assertTrue(
            IsClient().has_permission(self.request("GET", self.client_user), view)
        )
        self.assertFalse(
            IsClient().has_permission(self.request("GET", self.therapist), view)
        )
        self.assertTrue(
            IsTherapist().has_permission(self.request("GET", self.therapist), view)
        )
        self.assertFalse(
            IsTherapist().has_permission(self.request("GET", self.client_user), view)
        )
        self.assertTrue(
            IsAdminUser().has_permission(self.request("GET", self.admin), view)
        )
        self.assertFalse(
            IsAdminUser().has_permission(self.request("GET", self.client_user), view)
        )

    def test_therapist_permissions_allow_authenticated_safe_methods_only(self):
        permission = TherapistPermissions()

        self.assertTrue(
            permission.has_permission(self.request("GET", self.client_user), None)
        )
        self.assertFalse(
            permission.has_permission(self.request("POST", self.client_user), None)
        )
        self.assertFalse(
            permission.has_permission(self.request("GET", AnonymousUser()), None)
        )
