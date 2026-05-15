def serialize_office_location(office) -> dict | None:
    if office is None:
        return None
    localization = office.localization
    return {
        "name": localization.name,
        "city": localization.city,
        "address": localization.address,
        "postal_code": localization.postal_code,
        "room_number": office.room_number,
    }
