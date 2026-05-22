#!/bin/sh
set -e

python manage.py wait_for_db
python manage.py migrate

if [ "$SKIP_STARTUP" != "1" ]; then
  if [ "$SEED_IF_EMPTY" = "1" ]; then
    python manage.py seed_if_empty
  fi

  if [ "$COLLECT_STATIC" = "1" ]; then
    python manage.py collectstatic --noinput
  fi
fi

exec "$@"
