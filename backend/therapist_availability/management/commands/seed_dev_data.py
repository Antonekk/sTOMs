from datetime import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from offices.models import Localization, Office

from therapist_availability.models import AvailabilityBlock, Therapist
from therapist_availability.services import ScheduleService

User = get_user_model()

DEV_PASSWORD = "devpass123"

SCHEDULED_THERAPIST = {
    "email": "therapist.scheduled@dev.local",
    "phone_number": "+48200000001",
    "first_name": "Anna",
    "last_name": "Grafik",
}

EMPTY_THERAPIST = {
    "email": "therapist.empty@dev.local",
    "phone_number": "+48200000002",
    "first_name": "Bartosz",
    "last_name": "Pusty",
}

WEEKDAY_SCHEDULE = [
    {"day_of_week": day, "start_time": time(9, 0), "end_time": time(17, 0)}
    for day in range(5)
]


class Command(BaseCommand):
    help = "Seed development therapists (one with schedule, one without)."

    @transaction.atomic
    def handle(self, *args, **options):
        scheduled_user, scheduled_profile = self._create_therapist(**SCHEDULED_THERAPIST)
        ScheduleService.replace_base_schedule(scheduled_profile, WEEKDAY_SCHEDULE)

        empty_user, _empty_profile = self._create_therapist(**EMPTY_THERAPIST)

        self.stdout.write(self.style.SUCCESS("Development data seeded."))
        self.stdout.write("")
        self.stdout.write("Therapist with schedule (Mon–Fri 09:00–17:00):")
        self._print_credentials(scheduled_user)
        self.stdout.write("")
        self.stdout.write("Therapist with no schedule:")
        self._print_credentials(empty_user)
        self.stdout.write("")
        self.stdout.write(f"Password for both accounts: {DEV_PASSWORD}")

    def _create_therapist(self, *, email, phone_number, first_name, last_name):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "phone_number": phone_number,
                "first_name": first_name,
                "last_name": last_name,
                "role": User.Role.THERAPIST,
                "is_verified": True,
                "is_active": True,
            },
        )
        if created:
            user.set_password(DEV_PASSWORD)
            user.save(update_fields=["password"])
        else:
            user.phone_number = phone_number
            user.first_name = first_name
            user.last_name = last_name
            user.role = User.Role.THERAPIST
            user.is_verified = True
            user.is_active = True
            user.set_password(DEV_PASSWORD)
            user.save()

        therapist, therapist_created = Therapist.objects.get_or_create(user=user)
        if therapist_created or therapist.office is None:
            localization = Localization.objects.create(
                name=f"Lokalizacja {email}",
                city="Warszawa",
                postal_code="00-001",
                address="ul. Testowa 1",
            )
            office = Office.objects.create(localization=localization, room_number="101")
            therapist.office = office
            therapist.save(update_fields=["office"])

        AvailabilityBlock.objects.filter(
            therapist=therapist,
            type=AvailabilityBlock.BlockType.BASE,
        ).delete()

        return user, therapist

    def _print_credentials(self, user):
        self.stdout.write(f"  email: {user.email}")
