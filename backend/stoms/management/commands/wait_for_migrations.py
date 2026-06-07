#https://docs.djangoproject.com/en/6.0/howto/custom-management-commands/

import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError


class Command(BaseCommand):
    help = "Czeka, aż wszystkie migracje zostaną zastosowane (np. przez backend)."

    def handle(self, *args, **options):
        max_attempts = 60
        for attempt in range(1, max_attempts + 1):
            try:
                call_command("migrate", "--check", verbosity=0)
                self.stdout.write(self.style.SUCCESS("Migracje są aktualne."))
                return
            except SystemExit:
                self.stdout.write(
                    f"Próba {attempt}/{max_attempts} — oczekuję na migracje..."
                )
                time.sleep(2)
            except ProgrammingError:
                self.stdout.write(
                    f"Próba {attempt}/{max_attempts} — schemat bazy jeszcze nie istnieje..."
                )
                time.sleep(2)

        self.stderr.write(
            self.style.ERROR(
                f"Migracje nie zostały zastosowane po {max_attempts} próbach."
            )
        )
        raise SystemExit(1)
