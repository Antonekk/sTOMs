import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

NAME_REGEX = re.compile(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŻżŹź]+$")


def validate_only_letters(value: str):
    if not NAME_REGEX.match(value):
        raise ValidationError(
            _("Pole może zawierać wyłącznie litery alfabetu."),
            code="invalid_name",
        )
