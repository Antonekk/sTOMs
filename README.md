# sTOMs

Speech Therapy Office Management System

## Uruchomienie

Wymagania: Docker + Docker Compose (V2).
(Testowane pod Ubuntu (24.04))

### Dev

```bash
docker compose up --build
```

| Serwis | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| Storybook | http://localhost:6006 |
| Backend API | http://localhost:8000/api/v1/ |
| Admin Django | http://localhost:8000/admin/ |

Przy pierwszym starcie (pusta baza) tworzone są konta testowe:

| Rola | Email | Hasło |
|------|-------|-------|
| Admin | `admin@stoms.local` | `admin123` |
| Terapeuta | `terapeuta@stoms.local` | `dev123456` |
| Klient | `klient@stoms.local` | `dev123456` |

Żeby ponownie wykonać proces seedowania należy wykonać: `docker compose down -v` i ponownie `docker compose up --build`.

### Prod

Uzupełnij `.env.prod` i `.env` (m.in. `SECRET_KEY`, `ALLOWED_HOSTS`, dane SMTP) 

Przykładowy plik `.env`
```
# Przykładowo korzystając z smtp google
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=mojemail@gmail.com
EMAIL_HOST_PASSWORD=haslohaslohaslo
```

a nstępnie wykonaj:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Aplikacja odpalona zostanie pod http://localhost (nginx, port 80).

Przy uruchomieniu aplikacji w trybie produkcyjnym pomijane jest seedowanie, dane należy dodać ręcznie a superusera utworzyć bezpośrednio w kontenerze przy pomocy:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Testy

### Backend (Django)

Przy uruchomieniu wersji dev:

```bash
docker compose exec backend python manage.py test
```

Można testować również pojedyńcze moduły:

```bash
docker compose exec backend python manage.py test users
```

Django tworzy osobną bazę testową, więc dane testowe nie są trwale zapisywane.

## Storybook

Storybook służy do izolowanego podglądu i testów komponentów. Uruchamia się przy setupie dev pod http://localhost:6006.

## Uruchomienie lokalne (bez Dockera)


```bash
cd backend
pip install -r requirements.txt
python manage.py test
```

## References
- Logo (https://logoipsum.com/)
- Frontend React + JWT + AXIOS + React Router: setup (https://dev.to/sanjayttg/jwt-authentication-in-react-with-react-router-1d03)
