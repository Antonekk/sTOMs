from types import SimpleNamespace

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from users.permissions import IsAdminUser, IsClient, IsTherapist

from .helpers import create_client, create_superuser, create_therapist


class UserPermissionsTestCase(TestCase):
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
