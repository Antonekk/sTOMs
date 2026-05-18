from itertools import count

from offices.models import Localization, Office

_loc_counter = count(1)
_room_counter = count(1)


def create_localization(name=None):
    return Localization.objects.create(
        name=name or f"L{next(_loc_counter)}",
        city="City",
        postal_code="00-001",
        address="Addr",
    )


def create_office(*, localization=None, room_number=None):
    localization = localization or create_localization()
    return Office.objects.create(
        localization=localization,
        room_number=room_number or str(next(_room_counter)),
    )
