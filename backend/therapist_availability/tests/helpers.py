from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from offices.models import Localization, Office

from therapist_availability.models import Therapist

User = get_user_model()


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


def create_therapist(email="therapist@test.com", phone_number="+48123456789"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number=phone_number,
        first_name="Test",
        last_name="Therapist",
        role=User.Role.THERAPIST,
    )
    localization = Localization.objects.create(
        name=f"Lokalizacja {email}",
        city="Warszawa",
        postal_code="00-001",
        address="ul. Testowa 1",
    )
    office = Office.objects.create(localization=localization, room_number="101")
    therapist = Therapist.objects.create(user=user, office=office)
    return user, therapist
