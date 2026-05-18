from datetime import date
from itertools import count

from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()
_phone_counter = count(111111111)
_name_counter = count(0)

PASSWORD = "testpass123"


def _next_first_name():
    return chr(ord("A") + next(_name_counter))


def create_client(email="c@test.com", **extra_fields):
    defaults = {
        "password": PASSWORD,
        "phone_number": f"+48{next(_phone_counter)}",
        "first_name": "A",
        "last_name": "B",
        "role": User.Role.CLIENT,
    }
    defaults.update(extra_fields)
    return User.objects.create_user(email=email, **defaults)


def create_patient(user, **extra_fields):
    defaults = {
        "last_name": "X",
        "date_of_birth": date(2018, 4, 15),
        "is_primary": False,
        "is_active": True,
    }
    if "first_name" not in extra_fields:
        defaults["first_name"] = _next_first_name()
    defaults.update(extra_fields)
    return Patient.objects.create(user=user, **defaults)
