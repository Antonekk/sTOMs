export const API_URL = import.meta.env.VITE_API_URL as string | undefined

export const AUTH_ENDPOINTS = {
    REGISTER: "/api/users/",
    LOGIN: "/api/jwt/create/",
    REFRESH: "/api/jwt/refresh/",
    ACTIVATE: "/api/users/activation/",
    ME: "api/users/me/",
}