#!/bin/sh


set -e

if [ "$DATABASE" = "postgres" ]; then
  echo "Waiting for PostgreSQL at $PG_HOST:$PG_PORT..."

  while ! nc -z "$PG_HOST" "$PG_PORT"; do
    sleep 0.1
  done

  echo "PostgreSQL is available"
fi

if [ "$SKIP_STARTUP_TASKS" != "1" ]; then
  python manage.py migrate
  python manage.py spectacular --color --file schema.yml
fi

exec "$@"