from datetime import timedelta
from itertools import count

from django.contrib.auth import get_user_model
from django.utils import timezone
from offices.models import Localization, Office

from therapist_availability.models import Therapist

User = get_user_model()
_phone_counter = count(111111111)
_loc_counter = count(1)

PASSWORD = "testpass123"


def next_monday(from_date=None):
    from_date = from_date or timezone.localdate()
    days_ahead = (7 - from_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return from_date + timedelta(days=days_ahead)


def next_weekday(weekday, from_date=None):
    from_date = from_date or timezone.localdate()
    days_ahead = (weekday - from_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return from_date + timedelta(days=days_ahead)


def create_therapist(email="t@test.com"):
    user = User.objects.create_user(
        email=email,
        password=PASSWORD,
        phone_number=f"+48{next(_phone_counter)}",
        first_name="A",
        last_name="B",
        role=User.Role.THERAPIST,
    )
    localization = Localization.objects.create(
        name=f"L{next(_loc_counter)}",
        city="City",
        postal_code="00-001",
        address="Addr",
    )
    office = Office.objects.create(localization=localization, room_number="101")
    therapist = Therapist.objects.create(user=user, office=office)
    return user, therapist


def create_client(email="c@test.com"):
    return User.objects.create_user(
        email=email,
        password=PASSWORD,
        phone_number=f"+48{next(_phone_counter)}",
        first_name="C",
        last_name="D",
        role=User.Role.CLIENT,
    )
