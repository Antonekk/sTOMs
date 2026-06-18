import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from decouple import config
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("DJANGO_SECRET_KEY", "")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "PASSWORD_RESET_CONFIRM_URL": "haslo/reset/potwierdz/{uid}/{token}",
    "EMAIL_FRONTEND_PROTOCOL": config("EMAIL_FRONTEND_PROTOCOL", default="http"),
    "EMAIL_FRONTEND_DOMAIN": config("EMAIL_FRONTEND_DOMAIN", default="localhost:5173"),
    "EMAIL_FRONTEND_SITE_NAME": config("EMAIL_FRONTEND_SITE_NAME", default="sTOMs"),
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "ACTIVATION_URL": "aktywacja/{uid}/{token}",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "TOKEN_MODEL": None,
    "SERIALIZERS": {
        "user": "users.serializers.AppUserSerializer",
        "user_create_password_retype": "users.serializers.AppUserCreatePasswordRetypeSerializer",
        "current_user": "users.serializers.AppUserSerializer",
    },
}

_redis_url = os.environ.get("REDIS_URL") or os.environ.get(
    "CELERY_BROKER_URL", "redis://redis:6379/0"
)

CONSTANCE_BACKEND = "constance.backends.redisd.RedisBackend"
CONSTANCE_REDIS_CONNECTION = _redis_url
CONSTANCE_CONFIG = {
    "APPOINTMENT_GENERATION_DAYS": (14, "Ile dni w przód generować wizyty"),
    "APPOINTMENT_BOOKING_DAYS": (7, "Ile dni w przód można rezerwować"),
    "AVAILABILITY_MAX_RANGE_DAYS": (14, "Maksymalny zakres zapytań GET /availability"),
    "CANCELLATION_WINDOW_HOURS": (6, "Minimalny czas przed wizytą do anulowania (godz.)"),
    "REMINDER_HOURS_BEFORE": (24, "Ile godzin przed wizytą wysłać przypomnienie"),
    "MAX_PATIENTS_PER_CLIENT": (5, "Maksymalna liczba aktywnych pacjentów na klienta"),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "sTOMs",
    "DESCRIPTION": "Speech therapy office management system",
    "VERSION": "1.0.0",
    "ENUM_NAME_OVERRIDES": {
        "AppointmentSeriesStatusEnum": "reservations.models.AppointmentSeries.Status",
        "AppointmentStatusEnum": "reservations.models.Appointment.Status",
    },
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "jwtAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "SECURITY": [{"jwtAuth": []}],
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "djoser",
    "constance",
    "stoms",
    "users",
    "patients",
    "therapist_availability",
    "offices",
    "reservations",
    "notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stoms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "stoms.wsgi.application"


def _database_from_url(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username,
        "PASSWORD": parsed.password,
        "HOST": parsed.hostname,
        "PORT": str(parsed.port or 5432),
    }


def _database_config() -> dict:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return _database_from_url(database_url)

    return {
        "ENGINE": os.environ.get("DB_DRIVER", "django.db.backends.sqlite3"),
        "USER": os.environ.get("PG_USER", "postgres"),
        "PASSWORD": os.environ.get("PG_PASSWORD", "postgres"),
        "NAME": os.environ.get("PG_DB", str(BASE_DIR / "db.sqlite3")),
        "PORT": os.environ.get("PG_PORT", "5432"),
        "HOST": os.environ.get("PG_HOST", "localhost"),
    }


DATABASES = {"default": _database_config()}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

CELERY_BROKER_URL = _redis_url
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", _redis_url)
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "send-appointment-reminders": {
        "task": "notifications.tasks.send_appointment_reminders",
        "schedule": timedelta(hours=1),
    },
    "extend-appointment-horizons": {
        "task": "reservations.tasks.extend_appointment_horizons",
        "schedule": timedelta(days=1),
    },
}

AUTH_USER_MODEL = "users.AppUser"

EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER or "noreply@localhost",
)

if EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOWS_CREDENTIALS = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
