from datetime import date, time, timedelta
from itertools import count

from django.contrib.auth import get_user_model
from django.utils import timezone
from offices.models import Localization, Office
from patients.models import Patient
from reservations.models import Appointment, AppointmentSeries, AppointmentType
from therapist_availability.models import Therapist

User = get_user_model()
_phone_counter = count(111111111)
_type_counter = count(1)
_loc_counter = count(1)


def _next_phone() -> str:
    return f"+48{next(_phone_counter)}"


def create_therapist(email="t@test.com"):
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number=_next_phone(),
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
    user = User.objects.create_user(
        email=email,
        password="testpass123",
        phone_number=_next_phone(),
        first_name="C",
        last_name="D",
        role=User.Role.CLIENT,
    )
    patient = Patient.objects.create(
        user=user,
        first_name="E",
        last_name="F",
        date_of_birth=date(2018, 4, 15),
        is_primary=True,
    )
    return user, patient


def create_series(*, therapist, patient, is_weekly=False):
    appointment_type = AppointmentType.objects.create(
        name=f"T{next(_type_counter)}",
        duration_time_minutes=50,
        price="150.00",
        is_periodic=is_weekly,
    )
    target_date = timezone.localdate() + timedelta(days=7)
    series = AppointmentSeries.objects.create(
        therapist=therapist,
        patient=patient,
        appointment_type=appointment_type,
        start_time=time(10, 0),
        end_time=time(10, 50),
        start_date=target_date,
        is_weekly=is_weekly,
    )
    appointment = Appointment.objects.create(
        appointment_series=series,
        therapist=therapist,
        patient=patient,
        appointment_date=target_date,
        final_price=appointment_type.price,
    )
    return series, appointment, appointment_type
