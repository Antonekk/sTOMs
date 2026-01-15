def normalize_name(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    return value[0].upper() + value[1:].lower()
