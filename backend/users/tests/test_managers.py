from django.contrib.auth import get_user_model
from django.test import TestCase

from .helpers import PASSWORD, create_client, create_superuser

User = get_user_model()


class UserManagersTestCase(TestCase):
    def test_create_user(self):
        user = create_client()

        self.assertEqual(user.email, "c@test.com")
        self.assertEqual(user.get_full_name(), "A B")
        self.assertTrue(user.check_password(PASSWORD))
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
            User.objects.create_user(email="c2@test.com")
        with self.assertRaises(TypeError):
            User.objects.create_user(email="", phone_number="+48111111111")

    def test_create_superuser(self):
        admin_user = create_superuser()

        self.assertEqual(admin_user.email, "a@test.com")
        self.assertEqual(admin_user.get_full_name(), "E F")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.role, User.Role.ADMIN)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass

        with self.assertRaises(ValueError):
            create_superuser(email="a2@test.com", is_staff=False)
        with self.assertRaises(ValueError):
            create_superuser(email="a3@test.com", is_superuser=False)
