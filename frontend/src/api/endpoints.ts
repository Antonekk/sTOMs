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