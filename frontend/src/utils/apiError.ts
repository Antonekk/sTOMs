import axios from "axios";

const STATUS_MESSAGES: Record<number, string> = {
    400: "Nieprawidłowe dane formularza. Sprawdź wybrane opcje i spróbuj ponownie.",
    403: "Brak uprawnień do wykonania tej operacji.",
    404: "Nie znaleziono żądanego zasobu.",
    409: "Wybrany termin jest niedostępny lub koliduje z inną rezerwacją.",
    422: "Nie udało się przetworzyć żądania. Sprawdź wprowadzone dane.",
    500: "Błąd serwera. Spróbuj ponownie za chwilę.",
};

const FIELD_LABELS: Record<string, string> = {
    patient_id: "Pacjent",
    therapist_id: "Terapeuta",
    appointment_type_id: "Typ wizyty",
    start_date: "Data rozpoczęcia",
    start_time: "Godzina",
    is_weekly: "Rezerwacja cykliczna",
    date_from: "Data od",
    date_to: "Data do",
    day_of_week: "Dzień tygodnia",
    detail: "Błąd",
    non_field_errors: "Błąd",
};

const extractMessage = (value: unknown): string | null => {
    if (value === null || value === undefined) {
        return null;
    }
    if (typeof value === "string") {
        const trimmed = value.trim();
        return trimmed.length > 0 ? trimmed : null;
    }
    if (typeof value === "number" || typeof value === "boolean") {
        return String(value);
    }
    if (Array.isArray(value)) {
        const parts = value
            .map(extractMessage)
            .filter((part): part is string => part !== null);
        return parts.length > 0 ? parts.join(" ") : null;
    }
    if (typeof value === "object") {
        const record = value as Record<string, unknown>;
        if ("detail" in record) {
            return extractMessage(record.detail);
        }
        if ("message" in record) {
            return extractMessage(record.message);
        }
        const nested = Object.values(record)
            .map(extractMessage)
            .filter((part): part is string => part !== null);
        return nested.length > 0 ? nested.join(" ") : null;
    }
    return null;
};

const collectFieldErrors = (data: Record<string, unknown>): string[] => {
    const messages: string[] = [];

    for (const [field, value] of Object.entries(data)) {
        if (field === "detail") {
            continue;
        }
        const text = extractMessage(value);
        if (!text) {
            continue;
        }
        const label = FIELD_LABELS[field];
        messages.push(label ? `${label}: ${text}` : text);
    }

    return messages;
};

const isHtmlBody = (text: string): boolean =>
    text.startsWith("<!DOCTYPE") || text.startsWith("<html");

export const getApiErrorMessage = (
    err: unknown,
    fallback: string,
): string => {
    if (!axios.isAxiosError(err)) {
        return err instanceof Error && err.message ? err.message : fallback;
    }

    const status = err.response?.status;
    const data = err.response?.data;

    if (data === undefined || data === null || data === "") {
        if (status && STATUS_MESSAGES[status]) {
            return STATUS_MESSAGES[status];
        }
        return fallback;
    }

    if (typeof data === "string") {
        const trimmed = data.trim();
        if (!trimmed || isHtmlBody(trimmed)) {
            return status && STATUS_MESSAGES[status]
                ? STATUS_MESSAGES[status]
                : fallback;
        }
        return trimmed.length > 300 ? `${trimmed.slice(0, 300)}…` : trimmed;
    }

    if (Array.isArray(data)) {
        const text = extractMessage(data);
        if (text) {
            return text;
        }
        return status && STATUS_MESSAGES[status]
            ? STATUS_MESSAGES[status]
            : fallback;
    }

    if (typeof data === "object") {
        const record = data as Record<string, unknown>;

        const detailMessage = extractMessage(record.detail);
        if (detailMessage) {
            return detailMessage;
        }

        const fieldMessages = collectFieldErrors(record);
        if (fieldMessages.length > 0) {
            return fieldMessages.join(" ");
        }
    }

    if (status && STATUS_MESSAGES[status]) {
        return STATUS_MESSAGES[status];
    }

    return fallback;
};

export interface ApiErrorDisplay {
    title: string;
    description: string;
}

export const getApiErrorDisplay = (
    err: unknown,
    options: {
        fallback: string;
        title?: string;
        context?: "booking" | "availability" | "cancel" | "generic";
    },
): ApiErrorDisplay => {
    const description = getApiErrorMessage(err, options.fallback);
    const status = axios.isAxiosError(err) ? err.response?.status : undefined;

    const contextTitles: Record<string, Record<number | "default", string>> = {
        booking: {
            409: "Termin niedostępny",
            400: "Nie można utworzyć rezerwacji",
            default: options.title ?? "Nie udało się utworzyć rezerwacji",
        },
        availability: {
            400: "Nie można wyszukać terminów",
            default: options.title ?? "Nie udało się wyszukać terminów",
        },
        cancel: {
            409: "Nie można anulować wizyty",
            default: options.title ?? "Nie udało się anulować",
        },
        generic: {
            default: options.title ?? "Wystąpił błąd",
        },
    };

    const titles = contextTitles[options.context ?? "generic"];
    const title =
        (status !== undefined && titles[status]) || titles.default;

    return { title, description };
};
