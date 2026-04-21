export const API_URL = import.meta.env.VITE_API_URL as string | undefined

export const AUTH_ENDPOINTS = {
    REGISTER: "/api/users/",
    LOGIN: "/api/jwt/create/",
    REFRESH: "/api/jwt/refresh/",
    ACTIVATE: "/api/users/activation/",
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
}

export const RESERVATION_ENDPOINTS = {
    APPOINTMENT_TYPES: "/api/v1/appointment-types",
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