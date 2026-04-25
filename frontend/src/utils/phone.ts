/* Country code for Poland. */
export const PHONE_PREFIX = "+48";

/* Nine digits after the +48 country code. */
export const PHONE_LOCAL_PATTERN = /^\d{9}$/;

export function formatPhoneNumber(localDigits: string): string {
    return `${PHONE_PREFIX}${localDigits}`;
}

export const phoneLocalFormRules = [
    {
        required: true,
        message: "Podaj swój numer telefonu",
    },
    {
        pattern: PHONE_LOCAL_PATTERN,
        message: "Podaj poprawny numer telefonu (9 cyfr)",
    },
] as const;
