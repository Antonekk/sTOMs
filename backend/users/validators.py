import re
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

NAME_REGEX = re.compile(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŻżŹź]+$")


def validate_patient_age(value: date):
    today = date.today()
    age = (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )
    if age < 0:
        raise ValidationError(
            _("Niepoprawna data urodzenia"),
            code="patient_too_young",
        )
    if age > 100:
        raise ValidationError(
            _("Pacjent nie może mieć więcej niż 100 lat."),
            code="patient_too_old",
        )


def validate_patient_age_primary(value: date):
    today = date.today()
    age = (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )
    if age < 18:
        raise ValidationError(
            _("Główny pacjent musi być pełnoletni"),
            code="patient_too_young",
        )
    if age > 100:
        raise ValidationError(
            _("Pacjent nie może mieć więcej niż 100 lat."),
            code="patient_too_old",
        )
    return value


def validate_only_letters(value: str):
    if not NAME_REGEX.match(value):
        raise ValidationError(
            _("Pole może zawierać wyłącznie litery alfabetu."),
            code="invalid_name",
        )
