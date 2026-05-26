# sTOMs

Speech Therapy Office Management System

## Uruchomienie

Wymagania: Docker + Docker Compose v2.

### Dev

```bash
docker compose up --build
```

| Serwis | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/v1/ |
| Admin Django | http://localhost:8000/admin/ |

Przy pierwszym starcie (pusta baza) tworzone są konta testowe:

| Rola | Email | Hasło |
|------|-------|-------|
| Admin | `admin@stoms.local` | `admin123` |
| Terapeuta | `terapeuta@stoms.local` | `dev123456` |
| Klient | `klient@stoms.local` | `dev123456` |

Żeby dokonać ponownego seedowania należy: `docker compose down -v` i ponownie `docker compose up --build`.

### Prod

Uzupełnij `.env.prod` i `.env` (m.in. `SECRET_KEY`, `ALLOWED_HOSTS`, dane SMTP), nstępnie:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Aplikacja pod http://localhost (nginx, port 80).

Przy uruchomieniu aplikacji w trybie prod nie występuje już seedowanie, dane należy dodać ręcznie a superusera utworzyć bezpośrednio w kontenerze:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Testy

### Backend (Django)

Przy uruchomionym stacku dev:

```bash
docker compose exec backend python manage.py test
```

Wybrane moduły:

```bash
docker compose exec backend python manage.py test users
```

Lokalnie bez dockera:

```bash
cd backend
pip install -r requirements.txt
python manage.py test
```

Django tworzy osobną bazę testową — dane dev nie są nadpisywane.

## References
- Logo (https://logoipsum.com/)
