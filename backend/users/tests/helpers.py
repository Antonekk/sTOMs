from itertools import count

from django.contrib.auth import get_user_model

User = get_user_model()
_phone_counter = count(111111111)

PASSWORD = "testpass123"
NEW_PASSWORD = "newtestpass123"


def _next_phone() -> str:
    return f"+48{next(_phone_counter)}"


def create_client(email="c@test.com", password=PASSWORD, **extra_fields):
    defaults = {
        "phone_number": _next_phone(),
        "first_name": "A",
        "last_name": "B",
        "role": User.Role.CLIENT,
    }
    defaults.update(extra_fields)
    return User.objects.create_user(email=email, password=password, **defaults)


def create_therapist(email="t@test.com", password=PASSWORD, **extra_fields):
    defaults = {
        "phone_number": _next_phone(),
        "first_name": "C",
        "last_name": "D",
        "role": User.Role.THERAPIST,
    }
    defaults.update(extra_fields)
    return User.objects.create_user(email=email, password=password, **defaults)


def create_superuser(email="a@test.com", password=PASSWORD, **extra_fields):
    defaults = {
        "phone_number": _next_phone(),
        "first_name": "E",
        "last_name": "F",
        "role": User.Role.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    }
    defaults.update(extra_fields)
    return User.objects.create_superuser(email=email, password=password, **defaults)
