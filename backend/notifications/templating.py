from django.template.loader import render_to_string

WEEKDAY_LABELS = [
    "poniedziałek",
    "wtorek",
    "środa",
    "czwartek",
    "piątek",
    "sobota",
    "niedziela",
]


def weekday_label(date_value) -> str:
    return WEEKDAY_LABELS[date_value.weekday()]


def format_time(time_value) -> str:
    return time_value.strftime("%H:%M")


def format_date(date_value) -> str:
    return date_value.isoformat()


def format_bulk_dates(dates: list) -> str:
    formatted = [format_date(date_value) for date_value in sorted(dates)]
    if len(formatted) <= 3:
        return ", ".join(formatted)
    remaining = len(formatted) - 3
    return f"{formatted[0]}, {formatted[1]}, {formatted[2]} i {remaining} kolejnych"


def render_notification(base_path: str, context: dict) -> tuple[str, str]:
    template_prefix = f"notifications/{base_path}"
    title = render_to_string(f"{template_prefix}/title.txt", context).strip()
    description = render_to_string(f"{template_prefix}/description.txt", context).strip()
    return title, description
