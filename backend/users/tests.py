from datetime import date
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from patients.models import Patient
from djoser.utils import encode_uid
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from .permissions import IsAdminUser, IsClient, IsTherapist
from .serializers import AppUserCreatePasswordRetypeSerializer, AppUserSerializer


User = get_user_model()

# Basic test users
TEST_PASSWORD = "BardzoBezpieczne123!"
CLIENT_USER = {
    "first_name": "Jan",
    "last_name": "Juzer",
    "email": "jan_juzer@dobry-mail.com",
    "phone_number": "+48123123123",
}

THERAPIST_USER = {
    "first_name": "Jacek",
    "last_name": "Terapeutyczny",
    "email": "jacek_terapeutyczny@dobry-mail.com",
    "phone_number": "+48123321123",
    "role": User.Role.THERAPIST,
}

ADMIN_USER = {
    "first_name": "Ada",
    "last_name": "Min",
    "email": "ada_min@dobry-mail.com",
    "phone_number": "+48123123321",
    "role": User.Role.ADMIN,
    "is_staff": True,
}


def _build_user_fields(defaults, extra_fields):
    fields = {**defaults, **extra_fields}
    return fields.pop("email"), fields.pop("phone_number"), fields


def create_client(password=TEST_PASSWORD, **extra_fields):
    email, phone_number, fields = _build_user_fields(CLIENT_USER, extra_fields)
    return User.objects.create_user(
        email=email,
        phone_number=phone_number,
        password=password,
        **fields,
    )


def create_therapist(password=TEST_PASSWORD, **extra_fields):
    email, phone_number, fields = _build_user_fields(THERAPIST_USER, extra_fields)
    return User.objects.create_user(
        email=email,
        phone_number=phone_number,
        password=password,
        **fields,
    )


def create_superuser(password=TEST_PASSWORD, **extra_fields):
    email, phone_number, fields = _build_user_fields(ADMIN_USER, extra_fields)
    return User.objects.create_superuser(
        email=email,
        phone_number=phone_number,
        password=password,
        **fields,
    )


class TestUserManagers(TestCase):
    def test_create_user(self):
        user = create_client()

        self.assertEqual(user.email, CLIENT_USER["email"])
        self.assertEqual(user.phone_number, CLIENT_USER["phone_number"])
        self.assertEqual(user.get_full_name(), "Jan Juzer")
        self.assertTrue(user.check_password(TEST_PASSWORD))
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
            User.objects.create_user(email=CLIENT_USER["email"])
        with self.assertRaises(TypeError):
            User.objects.create_user(
                email="", phone_number=CLIENT_USER["phone_number"]
            )

    def test_create_superuser(self):
        admin_user = create_superuser()

        self.assertEqual(admin_user.email, ADMIN_USER["email"])
        self.assertEqual(admin_user.get_full_name(), "Ada Min")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, User.Role.ADMIN)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass

        with self.assertRaises(ValueError):
            create_superuser(
                email="admin2@dobry-mail.com",
                phone_number="+48111111111",
                is_staff=False,
            )
        with self.assertRaises(ValueError):
            create_superuser(
                email="admin3@dobry-mail.com",
                phone_number="+48222222222",
                is_superuser=False,
            )


class TestAppUserModel(TestCase):
    def test_phone_number_requires_plus48_prefix(self):
        user = User(
            email="phone@test.com",
            phone_number="123456789",
            first_name="Jan",
            last_name="Kowalski",
        )

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_role_helpers_and_full_name(self):
        client = create_client()
        therapist = create_therapist()

        self.assertEqual(str(client), CLIENT_USER["email"])
        self.assertEqual(client.get_full_name(), "Jan Juzer")
        self.assertEqual(therapist.get_full_name(), "Jacek Terapeutyczny")
        self.assertTrue(client.is_client)
        self.assertFalse(client.is_therapist)
        self.assertTrue(therapist.is_therapist)
        self.assertFalse(therapist.is_client)


class TestAppUserSerializers(TestCase):
    def test_register_serializer_rejects_phone_without_plus48_prefix(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "phone@example.com",
                "phone_number": "123456789",
                "first_name": "Anna",
                "last_name": "Kowalska",
                "password": TEST_PASSWORD,
                "re_password": TEST_PASSWORD,
                "date_of_birth": date(1995, 5, 20),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_register_serializer_creates_primary_patient(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                **CLIENT_USER,
                "password": TEST_PASSWORD,
                "re_password": TEST_PASSWORD,
                "date_of_birth": date(1995, 5, 20),
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        patient = Patient.objects.get(user=user)
        self.assertEqual(patient.first_name, "Jan")
        self.assertEqual(patient.last_name, "Juzer")
        self.assertEqual(patient.date_of_birth, date(1995, 5, 20))
        self.assertTrue(patient.is_primary)

    def test_register_serializer_rejects_underage_primary_patient(self):
        serializer = AppUserCreatePasswordRetypeSerializer(
            data={
                "email": "child@example.com",
                "phone_number": "+48123456789",
                "first_name": "Jan",
                "last_name": "Kowalski",
                "password": TEST_PASSWORD,
                "re_password": TEST_PASSWORD,
                "date_of_birth": date.today(),
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)

    def test_user_serializer_exposes_role_and_patients(self):
        user = create_client()
        Patient.objects.create(
            user=user,
            first_name=CLIENT_USER["first_name"],
            last_name=CLIENT_USER["last_name"],
            date_of_birth=date(1995, 5, 20),
            is_primary=True,
        )

        data = AppUserSerializer(instance=user).data

        self.assertEqual(data["role"], User.Role.CLIENT)
        self.assertEqual(len(data["patients"]), 1)
        self.assertEqual(data["patients"][0]["first_name"], "Jan")


class TestUserPermissions(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client_user = create_client()
        self.therapist = create_therapist()
        self.admin = create_superuser()

    def request(self, method, user):
        request = getattr(self.factory, method.lower())("/")
        request.user = user
        return request

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


class TestAccountActivation(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_client()
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.uid = encode_uid(self.user.pk)
        self.token = default_token_generator.make_token(self.user)

    def test_activation_is_idempotent_and_sends_confirmation_once(self):
        url = reverse("user-activation")
        payload = {"uid": self.uid, "token": self.token}

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(len(mail.outbox), 1)

            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(len(mail.outbox), 1)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activation_rejects_invalid_token(self):
        response = self.client.post(
            reverse("user-activation"),
            {"uid": self.uid, "token": "invalid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class TestPasswordReset(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_client()

    def test_reset_password_request_returns_success(self):
        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            response = self.client.post(
                reverse("user-reset-password"),
                {"email": CLIENT_USER["email"]},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reset_password_confirm_changes_password(self):
        uid = encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        new_password = "NoweBardzoBezpieczne123!"

        response = self.client.post(
            reverse("user-reset-password-confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": new_password,
                "re_new_password": new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(self.user.check_password(TEST_PASSWORD))

    def test_reset_password_confirm_rejects_invalid_token(self):
        uid = encode_uid(self.user.pk)

        response = self.client.post(
            reverse("user-reset-password-confirm"),
            {
                "uid": uid,
                "token": "invalid-token",
                "new_password": "NoweBardzoBezpieczne123!",
                "re_new_password": "NoweBardzoBezpieczne123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
