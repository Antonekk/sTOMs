import time

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Czeka na gotowość bazy danych przed startem aplikacji."

    def handle(self, *args, **options):
        max_attempts = 30
        for attempt in range(1, max_attempts + 1):
            try:
                connection.ensure_connection()
                self.stdout.write(self.style.SUCCESS("Baza danych jest dostępna."))
                return
            except OperationalError:
                self.stdout.write(
                    f"Próba {attempt}/{max_attempts} — baza niedostępna, czekam..."
                )
                time.sleep(1)

        self.stderr.write(
            self.style.ERROR(
                f"Nie udało się połączyć z bazą po {max_attempts} próbach."
            )
        )
        raise SystemExit(1)
