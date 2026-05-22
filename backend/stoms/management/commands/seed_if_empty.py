from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from offices.models import Localization, Office
from patients.models import Patient
from reservations.models import AppointmentType
from therapist_availability.models import Therapist

User = get_user_model()

DEV_PASSWORD = "dev123456"


class Command(BaseCommand):
    help = "Tworzy dane startowe dev, jeśli baza jest pusta."

    def handle(self, *args, **options):
        if Office.objects.exists():
            self.stdout.write("Baza niepusta — pomijam seeding.")
            return

        self.stdout.write("Baza pusta — tworzę dane startowe...")

        centrum = Localization.objects.create(
            name="Gabinet Centrum",
            city="Warszawa",
            postal_code="00-001",
            address="ul. Testowa 1",
        )
        mokotow = Localization.objects.create(
            name="Gabinet Mokotów",
            city="Warszawa",
            postal_code="02-001",
            address="ul. Przykładowa 10",
        )
        office_centrum = Office.objects.create(localization=centrum, room_number="101")
        Office.objects.create(localization=centrum, room_number="102")
        Office.objects.create(localization=mokotow, room_number="201")

        AppointmentType.objects.create(
            name="Wizyta pojedyncza",
            duration_time_minutes=30,
            price="100.00",
            is_periodic=False,
        )
        AppointmentType.objects.create(
            name="Wizyta okresowa",
            duration_time_minutes=50,
            price="150.00",
            is_periodic=True,
        )

        User.objects.create_superuser(
            email="admin@stoms.local",
            password="admin123",
            phone_number="+48123456789",
            first_name="Admin",
            last_name="STOMs",
            is_verified=True,
        )

        therapist_user = User.objects.create_user(
            email="terapeuta@stoms.local",
            password=DEV_PASSWORD,
            phone_number="+48123456780",
            first_name="Anna",
            last_name="Terapeutka",
            role=User.Role.THERAPIST,
            is_verified=True,
        )
        Therapist.objects.create(user=therapist_user, office=office_centrum)

        client_user = User.objects.create_user(
            email="klient@stoms.local",
            password=DEV_PASSWORD,
            phone_number="+48123456781",
            first_name="Jan",
            last_name="Klient",
            role=User.Role.CLIENT,
            is_verified=True,
        )
        Patient.objects.create(
            user=client_user,
            first_name="Jan",
            last_name="Klient",
            date_of_birth=date(1990, 5, 15),
            is_primary=True,
        )

        self.stdout.write(self.style.SUCCESS("Seeding zakończony."))
        self.stdout.write(
            f"Terapeuta: terapeuta@stoms.local / {DEV_PASSWORD}\n"
            f"Klient: klient@stoms.local / {DEV_PASSWORD}"
        )
