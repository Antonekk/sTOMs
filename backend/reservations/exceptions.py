from rest_framework.exceptions import APIException


class ConflictError(APIException):
    status_code = 409
    default_detail = "Wybrany termin koliduje z istniejącą wizytą."
    default_code = "conflict"
