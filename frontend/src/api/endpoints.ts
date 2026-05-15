export const API_URL = import.meta.env.VITE_API_URL as string | undefined

export const AUTH_ENDPOINTS = {
    REGISTER: "/api/users/",
    LOGIN: "/api/jwt/create/",
    REFRESH: "/api/jwt/refresh/",
    ACTIVATE: "/api/users/activation/",
    RESET_PASSWORD: "/api/users/reset_password/",
    RESET_PASSWORD_CONFIRM: "/api/users/reset_password_confirm/",
    ME: "api/users/me/",
    CONFIG: "/api/config/",
}

export const THERAPIST_AVAILABILITY_ENDPOINTS = {
    SELF_SCHEDULE: "api/therapists/self/schedule",
    SELF_SCHEDULE_OVERRIDE: "api/therapists/self/schedule/override",
}

export const PATIENT_ENDPOINTS = {
    PATIENTS: "/api/patients/",
    PATIENT: (id: string) => `/api/patients/${id}/`,
    RESTORE_PATIENT: (id: string) => `/api/patients/${id}/restore/`,
}

export const RESERVATION_ENDPOINTS = {
    APPOINTMENT_TYPES: "/api/v1/appointment-types",
    THERAPISTS: "/api/v1/therapists",
    BOOKABLE_SLOTS: "/api/v1/reservations/slots",
    BOOKABLE_SLOT_TIME_OPTIONS: "/api/v1/reservations/slots/time-options",
    RESERVATIONS: "/api/v1/reservations",
    RESERVATION: (id: string) => `/api/v1/reservations/${id}`,
}

export const VISIT_ENDPOINTS = {
    VISITS: "/api/v1/visits",
    VISIT: (id: string) => `/api/v1/visits/${id}`,
    STATUS: (id: string) => `/api/v1/visits/${id}/status`,
    NOTE: (id: string) => `/api/v1/visits/${id}/note`,
    CANCEL: (id: string) => `/api/v1/visits/${id}/cancel`,
}

export const AVAILABILITY_ENDPOINT = "/api/availability"

export const NOTIFICATION_ENDPOINTS = {
    NOTIFICATIONS: "/api/v1/notifications",
    NOTIFICATION: (id: string) => `/api/v1/notifications/${id}`,
    NOTIFICATION_READ: (id: string) => `/api/v1/notifications/${id}/read`,
    NOTIFICATIONS_READ_ALL: "/api/v1/notifications/read",
}