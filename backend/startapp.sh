#!/bin/sh


set -e

if [ "$DATABASE" = "postgres" ]; then
  echo "Waiting for PostgreSQL at $SQL_HOST:$SQL_PORT..."

  while ! nc -z "$PG_HOST" "$PG_PORT"; do
    sleep 0.1
  done

  echo "PostgreSQL is available"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py spectacular --color --file schema.yml

exec "$@"