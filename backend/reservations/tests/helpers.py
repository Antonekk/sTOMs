from datetime import date, time, timedelta
from itertools import count

from django.contrib.auth import get_user_model
from django.utils import timezone
from offices.models import Localization, Office
from patients.models import Patient
from therapist_availability.engines import ScheduleEngine
from therapist_availability.models import Therapist

from reservations.models import Appointment, AppointmentSeries, AppointmentType

User = get_user_model()
_phone_counter = count(111111111)
_loc_counter = count(1)
_type_counter = count(1)

PASSWORD = "testpass123"


def future_monday(from_date=None):
    from_date = from_date or timezone.localdate()
    days_ahead = (0 - from_date.weekday()) % 7
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
    user = User.objects.create_user(
        email=email,
        password=PASSWORD,
        phone_number=f"+48{next(_phone_counter)}",
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


def create_appointment_types():
    periodic = AppointmentType.objects.create(
        name=f"T{next(_type_counter)}",
        duration_time_minutes=50,
        price="150.00",
        is_periodic=True,
    )
    one_time = AppointmentType.objects.create(
        name=f"T{next(_type_counter)}",
        duration_time_minutes=30,
        price="100.00",
        is_periodic=False,
    )
    return periodic, one_time


def add_weekly_schedule(therapist):
    ScheduleEngine.replace_base_schedule(
        therapist,
        [
            {"day_of_week": day, "start_time": time(9, 0), "end_time": time(17, 0)}
            for day in range(7)
        ],
    )


def create_series(*, therapist, patient, appointment_type, start_date, **extra_fields):
    defaults = {
        "start_time": time(10, 0),
        "end_time": time(10, 30),
        "start_date": start_date,
    }
    defaults.update(extra_fields)
    return AppointmentSeries.objects.create(
        therapist=therapist,
        patient=patient,
        appointment_type=appointment_type,
        **defaults,
    )


def create_appointment(*, series, therapist, patient, appointment_date, **extra_fields):
    defaults = {
        "final_price": series.appointment_type.price,
    }
    defaults.update(extra_fields)
    return Appointment.objects.create(
        appointment_series=series,
        therapist=therapist,
        patient=patient,
        appointment_date=appointment_date,
        **defaults,
    )
