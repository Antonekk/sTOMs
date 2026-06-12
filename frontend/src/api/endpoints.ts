export const API_URL = import.meta.env.VITE_API_URL as string | undefined

export const ADMIN_URL = API_URL ? `${API_URL}/admin/` : "/admin/"

export const AUTH_ENDPOINTS = {
    REGISTER: "/api/v1/users/",
    LOGIN: "/api/v1/jwt/create/",
    REFRESH: "/api/v1/jwt/refresh/",
    ACTIVATE: "/api/v1/users/activation/",
    RESET_PASSWORD: "/api/v1/users/reset_password/",
    RESET_PASSWORD_CONFIRM: "/api/v1/users/reset_password_confirm/",
    ME: "/api/v1/users/me/",
    CONFIG: "/api/v1/config/",
}

export const THERAPIST_AVAILABILITY_ENDPOINTS = {
    SELF_SCHEDULE: "/api/v1/therapists/self/schedule",
    SELF_SCHEDULE_OVERRIDE: "/api/v1/therapists/self/schedule/override",
}

export const OFFICE_ENDPOINTS = {
    LOCALIZATIONS: "/api/v1/localizations/",
}

export const PATIENT_ENDPOINTS = {
    PATIENTS: "/api/v1/patients/",
    PATIENT: (id: string) => `/api/v1/patients/${id}/`,
    RESTORE_PATIENT: (id: string) => `/api/v1/patients/${id}/restore/`,
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

export const NOTIFICATION_ENDPOINTS = {
    NOTIFICATIONS: "/api/v1/notifications",
    NOTIFICATION: (id: string) => `/api/v1/notifications/${id}`,
    NOTIFICATION_READ: (id: string) => `/api/v1/notifications/${id}/read`,
    NOTIFICATIONS_READ_ALL: "/api/v1/notifications/read",
}
