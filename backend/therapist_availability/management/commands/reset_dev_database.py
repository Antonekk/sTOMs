import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = "Drop and recreate the configured PostgreSQL database (development only)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("reset_dev_database is only allowed when DEBUG=True.")

        database = settings.DATABASES["default"]
        engine = database.get("ENGINE", "")

        if engine != "django.db.backends.postgresql":
            raise CommandError(
                "reset_dev_database requires PostgreSQL (django.db.backends.postgresql)."
            )

        db_name = database["NAME"]
        if not isinstance(db_name, str):
            raise CommandError("Database NAME must be a string for PostgreSQL reset.")

        self.stdout.write(self.style.WARNING(f"Recreating database {db_name!r}..."))

        connection = psycopg2.connect(
            dbname="postgres",
            user=database["USER"],
            password=database["PASSWORD"],
            host=database["HOST"],
            port=database["PORT"],
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    [db_name],
                )
                database_exists = cursor.fetchone() is not None

                if database_exists:
                    cursor.execute(
                        f'ALTER DATABASE "{db_name}" ALLOW_CONNECTIONS false'
                    )
                    cursor.execute(
                        """
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = %s AND pid <> pg_backend_pid()
                        """,
                        [db_name],
                    )
                    cursor.execute(f'DROP DATABASE "{db_name}"')

                cursor.execute(f'CREATE DATABASE "{db_name}"')
        finally:
            connection.close()

        self.stdout.write(self.style.SUCCESS(f"Database {db_name!r} recreated."))
